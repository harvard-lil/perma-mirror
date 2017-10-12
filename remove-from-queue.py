import boto3
import json
import sys


""" 
If a write to S3 fails after object creation, a message will get put on the queue and never deleted.
The symptom of this will be repeated lines in the syslog on the mirror like

  "WARNING: generated/warcs/12/34/56/1234-5678.warc.gz does not exist in the fnord bucket"

You can wait for the message to time out (currently four days), or delete it using this script. Stop
the mirror service, so there's no competition for queue items, then run this script with queue name and object
key as arguments, as many times as it takes to see the response "message deleted", something like this:

  python ./remove_from_queue.py fnord-queue generated/warcs/12/34/56/1234-5678.warc.gz
  
You may need to make or start a virtualenv in order to use boto3.
"""


sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=sys.argv[1])

for message in queue.receive_messages(MaxNumberOfMessages=10):
    key = None
    bucket = None
    event = None
    body = json.loads(message.body)
    try:
        record = body['Records'][0]
        key = record['s3']['object']['key']
        if key == sys.argv[2]:
            message.delete()
            print("message deleted")
    except KeyError:
        pass
