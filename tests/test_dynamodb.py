import pytest
import boto3
import os
from ptr_api.aws import dynamodb

# @pytest.fixture
# def sqs_mocker(scope='session', autouse=True):

#     dynamodb_r_mock = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url=f'http://localhost:5003')
#     dynamodb_c_mock = boto3.client('dynamodb', region_name='us-east-1', endpoint_url=f'http://localhost:5003')

#     table_name = 'test_table'

#     queue_url = dynamodb_c_mock.create_table(
#         QueueName=queue_name
#     )['QueueUrl']

#     yield (sqs_r_mock, sqs_c_mock, queue_url, queue_name)

# def test_create_table():
#     table_name = 'test_jackie'
#     table = dynamodb.create_table(table_name)

#     assert True

#def test_get_table():
#    return

#def test_insert_item():
#    return

#def test_get_item():
#    return

#def test_scan():
#    return

