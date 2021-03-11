import boto3
import botocore
import botocore.exceptions
import json
import time
from pathlib import Path
import click


@click.command()
@click.argument('queue')
@click.option('--messages', type=click.IntRange(1, 10), default=10,
              help='Messages per attempt')
@click.option('--directory', default=str(Path.cwd()),
              help='Base directory for downloaded files')
@click.option('--prefix', default='generated/warcs',
              help='Prefix for checking storage location')
@click.option('--skip', multiple=True, default=['generated/cache'],
              help='Prefixes to skip')
@click.option('--sleep', default=5,
              help='Time to sleep in seconds between attempts')
@click.option('--repeat/--no-repeat', default=True,
              help='Cycle indefinitely, or run once for testing')
@click.version_option()
def main(queue, messages, directory, prefix, skip, sleep, repeat):
    """
    This program watches an SQS queue and downloads newly-created S3 objects

    It assumes that you have AWS credentials set up correctly in ~/.aws/config,
    ~/.boto, or the like.
    """
    # connect to SQS
    sqs = boto3.resource('sqs')
    q = sqs.get_queue_by_name(QueueName=queue)
    # connect to S3
    s3 = boto3.resource('s3')

    base = Path(directory)
    # does it look like the storage is mounted? check on every download, too.
    storage_location = base / prefix
    assert storage_location.is_dir()
    click.echo(f'Downloading to {directory}')

    while True:
        for message in q.receive_messages(MaxNumberOfMessages=messages):
            key = None
            bucket = None
            event = None
            body = json.loads(message.body)
            try:
                record = body['Records'][0]
                key = record['s3']['object']['key']
                bucket = record['s3']['bucket']['name']
                event = record['eventName']
            except KeyError:
                pass

            if (
                    key
                    and bucket
                    and event.startswith('ObjectCreated')
                    and not any([key.startswith(s) for s in skip])
            ):
                subfolders = Path(key).parts[:-1]
                base.joinpath(*subfolders).mkdir(parents=True, exist_ok=True)
                try:
                    assert storage_location.is_dir()
                    s3.Bucket(bucket).download_file(key, str(base / key))
                    message.delete()
                    click.echo(f'Got {key} from {bucket}')
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        click.echo(f'WARNING: {key} is not in {bucket}')
                    elif e.response['Error']['Code'] == 'NoSuchKey':
                        click.echo(f'WARNING: NoSuchKey: {key}')
                    else:
                        raise
            else:
                click.echo(f'Deleting message {message.body}')
                message.delete()
        if repeat:
            time.sleep(sleep)
        else:
            return 0


if __name__ == '__main__':
    main()
