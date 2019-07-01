import pytest
from ptr_api.aws import s3

import boto3
from botocore.client import Config
from moto import mock_s3

import os
from os.path import join, dirname, isfile
from dotenv import load_dotenv


def test_aws_config_values_set():
    REGION = str(os.environ.get('REGION'))

    assert REGION is not None

@mock_s3
def test_boto3_connection():
    s3_connection = s3.get_boto3_s3()

    assert s3_connection is not None

@mock_s3
def test_get_presigned_post_url():
    with app.app_context():
        BUCKET_NAME = 'test_bucket'
        OBJECT_NAME = 'test_object'

        json_url = s3.get_presigned_post_url(BUCKET_NAME, OBJECT_NAME)
        print(json_url)

        assert True









