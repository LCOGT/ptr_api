import pytest
from ptr_api.aws import s3
from moto import mock_s3
from flask import Flask
import re

@mock_s3
def test_get_presigned_url():
    BUCKET_NAME = 'test_bucket'
    OBJECT_NAME = 'test_object'
    url = s3.get_presigned_url(BUCKET_NAME, OBJECT_NAME)

    verify_url = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] [!*\\(\\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    verify_region = re.search(s3.REGION, url)
    verify_bucket = re.search(BUCKET_NAME, url)
    verify_object = re.search(OBJECT_NAME, url)

    assert verify_url is not None
    assert verify_region is not None
    assert verify_bucket is not None
    assert verify_object is not None

        
@mock_s3
def test_get_presigned_url_error():
    with pytest.raises(Exception):
        assert s3.get_presigned_url(BUCKET_NAME)


@mock_s3
def test_get_presigned_post_url():
   app = Flask(__name__)
   with app.app_context():
       BUCKET_NAME = 'test_bucket'
       OBJECT_NAME = 'test_object'

       json_url = s3.get_presigned_post_url(BUCKET_NAME, OBJECT_NAME)

       assert True
