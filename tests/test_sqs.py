import pytest
import boto3
import os, random
from ptr_api.aws import sqs

@pytest.fixture
def sqs_mocker(scope='session', autouse=True):
    sqs_r_mock = boto3.resource('sqs', region_name='us-east-1', endpoint_url=f'http://localhost:5002')
    sqs_c_mock = boto3.client('sqs', region_name='us-east-1', endpoint_url=f'http://localhost:5002')

    queue_name = f"{random.randint(0,1000)}_tablename"

    queue_url = sqs_c_mock.create_queue(
        QueueName=queue_name
    )['QueueUrl']

    yield (sqs_r_mock, sqs_c_mock, queue_url, queue_name)


def test_get_queue_item(sqs_mocker):
    sqs_r_mock, sqs_c_mock, queue_url, queue_name = sqs_mocker
    message_body = 'why hello there'
    sqs_c_mock.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )
    sqs.sqs_r = sqs_r_mock
    sqs.sqs_c = sqs_c_mock
    
    result = sqs.get_queue_item(queue_name)

    assert result == message_body


def test_send_to_queue(sqs_mocker):
    sqs_r_mock, sqs_c_mock, queue_url, queue_name = sqs_mocker
    sqs.sqs_r = sqs_r_mock
    sqs.sqs_c = sqs_c_mock

    response = sqs.send_to_queue(queue_name)
    response_status_code = response['ResponseMetadata']['HTTPStatusCode']

    assert response_status_code == 200

