import boto3
import botocore
import botocore.exceptions
import json
import time
import os
import argparse


def main():
    """
    This program watches an SQS queue and downloads newly-created S3 objects

    It assumes that you have AWS credentials set up correctly in ~/.aws/config, ~/.boto, or the like.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('queue', help="SQS queue to poll")
    parser.add_argument('--messages', type=int, choices=xrange(1, 10), help="Messages per attempt", default=10)
    parser.add_argument('--directory', help="Base directory for downloaded files", default=os.getcwd())
    parser.add_argument('--sleep', type=int, help="Time to sleep in seconds between attempts", default=5)
    args = parser.parse_args()

    # connect to SQS
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=args.queue)
    # connect to S3
    s3 = boto3.resource('s3')

    print("Downloading to {0}".format(args.directory))

    while True:
        for message in queue.receive_messages(MaxNumberOfMessages=args.messages):
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

            if key and bucket and event.startswith("ObjectCreated"):
                try:
                    path, filename = os.path.split(key)
                    os.makedirs(os.path.join(args.directory, path))
                except OSError:
                    pass
                fullpath = os.path.join(args.directory, key)
                if os.path.exists(fullpath):
                    print("{0} already exists".format(key))
                    message.delete()
                else:
                    try:
                        s3.Bucket(bucket).download_file(key, fullpath)
                        message.delete()
                        print("Got {0} from {1}".format(key, bucket))
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            print("WARNING: {0} does not exist in the {1} bucket".format(key, bucket))
                        else:
                            raise
            else:
                print("Deleting message {0}".format(message.body))
                message.delete()

        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
