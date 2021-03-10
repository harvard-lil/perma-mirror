import pytest
from click.testing import CliRunner
from uuid import uuid4
import boto3
from perma_mirror.poll_for_warcs import main
from helpers import simulate_aws


runner = CliRunner()
keys = [
    'generated/warcs/AA/BB/CC/AABB-CCDD.tar.gz',
    'generated/cache/some/cache/file.txt',
    'generated/warcs/11/22/33/1122-3344.tar.gz',
    'generated/warcs/EE/FF/GG/EEFF-GGHH.tar.gz',
    'generated/warcs/EE/FF/GG/EEFF-GGHH.tar.gz',
]
events = ['ObjectCreated',
          'ObjectCreated',
          'SomeOtherEvent',
          'ObjectCreated',
          'ObjectCreated']
contents = [str(uuid4()) for n in range(5)]
messages = list(zip(keys, events))
objects = list(zip(keys, contents))


def test_help():
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'newly-created S3 object' in result.output


def test_nonexistent_queue(sqs, s3):
    with pytest.raises(sqs.exceptions.QueueDoesNotExist):
        runner.invoke(main,
                      ['--no-repeat',
                       'no_such_queue'],
                      catch_exceptions=False)


def test_cli(sqs, s3, tmp_path):
    # set up and check the "remote" part of the test harness...
    simulate_aws(sqs, s3, messages, objects)

    # check the queue
    msg_count = int(boto3.client('sqs').get_queue_attributes(
        QueueUrl=sqs.get_queue_url(QueueName='queue')['QueueUrl'],
        AttributeNames=['ApproximateNumberOfMessages']
    )['Attributes']['ApproximateNumberOfMessages'])
    assert msg_count == len(messages)

    # check the bucket (this would fail with over 1,000 objects)
    key_count = boto3.client('s3').list_objects_v2(Bucket='bucket')['KeyCount']
    assert key_count == len(set(keys))

    # then set up and check the local part
    storage = tmp_path / 'generated/warcs'
    storage.mkdir(parents=True)
    assert storage.is_dir()
    assert str(storage) == f'{tmp_path}/generated/warcs'

    # run the program
    result = runner.invoke(main,
                           ['--no-repeat',
                            '--directory', str(tmp_path.resolve()),
                            'queue'],
                           catch_exceptions=False)

    assert result.exit_code == 0

    expected_keys = set([
        m[0] for m in messages
        if m[1] == 'ObjectCreated'
        and not m[0].startswith('generated/cache')
    ])
    downloaded_keys = [
        str(x.relative_to(tmp_path))
        for x in tmp_path.glob('**/*')
        if x.is_file()
    ]
    assert sorted(expected_keys) == sorted(downloaded_keys)

    for key in downloaded_keys:
        p = tmp_path / key
        # if we had a duplicate key, the last object is the one we expect
        assert p.read_text() == [obj[1]
                                 for obj in objects
                                 if obj[0] == key][-1]
