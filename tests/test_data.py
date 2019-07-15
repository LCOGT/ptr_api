import pytest
import unittest.mock as mock
from ptr_api.endpoints import data
import flask


@mock.patch('ptr_api.endpoints.data.request')
def test_upload(mock_request):
   mock_request.get_data.return_value = '{"object_name": "raw_data/2019/a_file2.txt"}'
   response = data.upload('test_site')
   expected_response = "{'url': 'https://s3.amazonaws.com/None', 'fields': {'key': 'site1/raw_data/2019/a_file2.txt', 'x-amz-algorithm': 'AWS4-HMAC-SHA256', 'x-amz-credential': 'AKIAUOVR2PJKRTE4MRK6/20190709/us-east-1/s3/aws4_request', 'x-amz-date': '20190709T180802Z', 'policy': 'eyJleHBpcmF0aW9uIjogIjIwMTktMDctMDlUMTk6MDg6MDJaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAiTm9uZSJ9LCB7ImtleSI6ICJzaXRlMS9yYXdfZGF0YS8yMDE5L2FfZmlsZTIudHh0In0sIHsieC1hbXotYWxnb3JpdGhtIjogIkFXUzQtSE1BQy1TSEEyNTYifSwgeyJ4LWFtei1jcmVkZW50aWFsIjogIkFLSUFVT1ZSMlBKS1JURTRNUks2LzIwMTkwNzA5L3VzLWVhc3QtMS9zMy9hd3M0X3JlcXVlc3QifSwgeyJ4LWFtei1kYXRlIjogIjIwMTkwNzA5VDE4MDgwMloifV19', 'x-amz-signature': '4b0c2852e513e975c4712bd037d85e75e7d0bbba51e84fbf8113a6d78373db9e'}}"

   assert response == expected_response

@mock.patch('ptr_api.endpoints.data.request')
def test_download(mock_request):
    BUCKET_NAME = 'test_bucket'
   # mock_request.get_data.return_value =
    url = data.download('test_site')
    expected_url = 'need to figure out what goes here'

    assert url == expected_url