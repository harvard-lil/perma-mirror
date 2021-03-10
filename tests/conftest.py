import pytest
import os
from moto import mock_sqs, mock_s3
import boto3


@pytest.fixture(scope='package')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'


@pytest.fixture()
def sqs(aws_credentials):
    with mock_sqs():
        yield boto3.client('sqs')


@pytest.fixture()
def s3(aws_credentials):
    with mock_s3():
        yield boto3.client('s3')
