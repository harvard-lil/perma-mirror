import boto3
import json
import click


@click.command()
@click.argument('queue')
@click.argument('key')
def main(queue, key):
    """
    If a write to S3 fails after object creation, a message will get put on the
    queue and never deleted.

    The symptom of this will be repeated lines in the syslog on the mirror like

    "WARNING: generated/warcs/12/34/56/1234-5678.warc.gz does not exist
    in the fnord bucket"

    You can wait for the message to time out (currently four days), or delete
    it using this script. Stop the mirror service, so there's no competition
    for queue items, then run this script with queue name and object key as
    arguments, as many times as it takes to see the response "message deleted",
    something like this:

    remove-from-queue <queue> generated/warcs/12/34/56/1234-5678.warc.gz

    (This script is present for historical purposes.)
    """
    sqs = boto3.resource('sqs')
    q = sqs.get_queue_by_name(QueueName=queue)

    for message in q.receive_messages(MaxNumberOfMessages=10):
        current_key = None
        body = json.loads(message.body)
        try:
            record = body['Records'][0]
            current_key = record['s3']['object']['key']
            if current_key == key:
                message.delete()
                click.echo("message deleted")
        except KeyError:
            pass


if __name__ == '__main__':
    main()
