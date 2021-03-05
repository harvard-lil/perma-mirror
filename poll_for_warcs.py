import boto3
import botocore
import botocore.exceptions
import json
import time
import os
import click


@click.command()
@click.argument('queue')
@click.option('--messages', type=click.IntRange(1, 10), default=10,
              help='Messages per attempt')
@click.option('--directory', default=os.getcwd(),
              help='Base directory for downloaded files')
@click.option('--sleep', default=5,
              help='Time to sleep in seconds between attempts')
def main(queue, messages, directory, sleep):
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

    # does it look like the storage is mounted? check on every download, too.
    generated_warcs = f'{directory}/generated/warcs'
    assert os.path.isdir(generated_warcs)
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
                    and event.startswith("ObjectCreated")
                    and not key.startswith("generated/cache/")
            ):
                try:
                    path, filename = os.path.split(key)
                    os.makedirs(os.path.join(directory, path))
                except OSError:
                    pass
                fullpath = os.path.join(directory, key)
                try:
                    assert os.path.isdir(generated_warcs)
                    s3.Bucket(bucket).download_file(key, fullpath)
                    message.delete()
                    click.echo(f'Got {key} from {bucket}')
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        click.echo(f'WARNING: {key} is not in {bucket}')
                    elif e.response['Error']['Code'] == "NoSuchKey":
                        click.echo(f'WARNING: NoSuchKey: {key}')
                    else:
                        raise
            else:
                click.echo(f'Deleting message {message.body}')
                message.delete()

        time.sleep(sleep)


if __name__ == "__main__":
    main()
