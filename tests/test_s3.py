from ptr_api import environment
import pytest, re
from ptr_api.aws import s3

def test_get_presigned_url():
    BUCKET_NAME = 'test_bucket'
    OBJECT_NAME = 'test_object'
    url = s3.get_presigned_url(BUCKET_NAME, OBJECT_NAME)
    expected_url= "https://s3.amazonaws.com/" + BUCKET_NAME + '/' + OBJECT_NAME

    verify_url = re.search(expected_url, url)
    verify_region = re.search(s3.REGION, url)

    assert verify_url is not None
    assert verify_region is not None

def test_get_presigned_post_url():
    BUCKET_NAME = 'test_bucket'
    OBJECT_NAME = 'test_object'

    response_dict = s3.get_presigned_post_url(BUCKET_NAME, OBJECT_NAME)
    url = response_dict['url']
    expected_url = "https://s3.amazonaws.com/" + BUCKET_NAME

    assert url == expected_url
