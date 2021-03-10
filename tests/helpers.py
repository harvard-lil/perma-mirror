from datetime import datetime
import json
import io


bucket = 'bucket'


def simulate_aws(sqs, s3, messages, objects):
    """
    This function creates and populates a bucket and a queue.
    """
    sqs.create_queue(QueueName='queue')
    for msg in messages:
        _send_message(sqs, msg)
    s3.create_bucket(Bucket=bucket,
                     CreateBucketConfiguration={
                         'LocationConstraint': 'us-west-2'
                     })
    for obj in objects:
        _populate_bucket(s3, bucket, obj)


def _send_message(sqs, msg):
    response = sqs.get_queue_url(QueueName='queue')
    queue_url = response['QueueUrl']
    body = {
        'Records': [
            {
                's3': {
                    'object': {
                        'key': msg[0]
                    },
                    'bucket': {
                        'name': bucket
                    }
                },
                'eventName': msg[1]
            }
        ]
    }
    today = datetime.today().strftime('%Y-%m-%d')
    sqs.send_message(QueueUrl=queue_url,
                     MessageBody=json.dumps(body),
                     MessageAttributes={
                         'Date': {'DataType': 'String',
                                  'StringValue': today},
                         'QueryType': {'DataType': 'String',
                                       'StringValue': "RETRY"}
                     }, MessageGroupId='test-queue',
                     MessageDeduplicationId=f'{today}-A')


def _populate_bucket(s3, bucket, obj):
    f = io.BytesIO(bytes(obj[1], 'utf-8'))
    s3.upload_fileobj(f, bucket, obj[0])
