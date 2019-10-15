from ptr_api import environment
import pytest, re
import unittest.mock as mock
from ptr_api.endpoints import data
from flask import Flask
import json


@mock.patch('ptr_api.endpoints.data.request')
def test_upload(mock_request):
   app = Flask(__name__)
   with app.app_context():
       mock_request.get_data.return_value = '{"object_name": "raw_data/2019/a_file2.txt"}'
       response = data.upload('test_site')
       response_dict = json.loads(response.data.decode('utf8'))
       url = response_dict['url']
       expected_url = 'https://photonranch-001.s3.amazonaws.com/'

       assert url == expected_url


@mock.patch('ptr_api.endpoints.data.request')
def test_download(mock_request):
    mock_request.get_data.return_value = '{"object_name": "raw_data/2019/a_file2.txt"}'
    url = data.download('test_site')
    expected_url = 'https://photonranch-001.s3.amazonaws.com/test_site/raw_data/2019/a_file2.txt'
    verify_url = re.search(expected_url, url)

    assert verify_url is not None