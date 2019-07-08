import pytest
import unittest.mock as mock
from ptr_api.endpoints import commands
import flask

@mock.patch('ptr_api.aws.sqs.get_queue_item')
def test_get_command(mock_get_queue_item):
    mock_get_queue_item.return_value = {"device": "mount_1", "ra": 0, "dec": -52, "command": "goto", "timestamp": "1562621940"}
    content = commands.get_command('test_site')
    expected_content = {'device': 'mount_1', 'ra': 0, 'dec': -52, 'command': 'goto', 'timestamp': '1562621940'}

    assert content == expected_content


@mock.patch('ptr_api.aws.sqs.get_queue_item')
def test_get_command_missing_queue(mock_get_queue_item):
    mock_get_queue_item.return_value = False
    content = commands.get_command('test_site')
    expected_content = '{"Body": "empty"}'

    assert content == expected_content


app = flask.Flask(__name__)
with app.test_request_context():
@mock.patch.object(flask.request, 'get_data')
@mock.patch('ptr_api.aws.sqs.send_to_queue')
def test_post_command(mock_send_to_queue, mock_flask_response):
    mock_send_to_queue.return_value = {'MD5OfMessageBody': '86c11591bad61ffac08e4bfdd0959b84', 'MessageId': 'a5e57b55-49d4-4548-a885-7e879d5c331f', 'SequenceNumber': '166420728385957740544', 'ResponseMetadata': {'RequestId': 'c2d37c86-cdeb-5d3b-8a6a-291b0c0790f8', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'c2d37c86-cdeb-5d3b-8a6a-291b0c0790f8', 'date': 'Mon, 08 Jul 2019 22:11:56 GMT', 'content-type': 'text/xml', 'content-length': '432'}, 'RetryAttempts': 0}}
    mock_flask_response = {'device': 'mount_1', 'ra': 4, 'dec': 60, 'command': 'goto', 'timestamp': '1562625931'}

    response = commands.post_command('test_site')
    expected_response = "{'MD5OfMessageBody': '86c11591bad61ffac08e4bfdd0959b84', 'MessageId': 'a5e57b55-49d4-4548-a885-7e879d5c331f', 'SequenceNumber': '166420728385957740544', 'ResponseMetadata': {'RequestId': 'c2d37c86-cdeb-5d3b-8a6a-291b0c0790f8', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'c2d37c86-cdeb-5d3b-8a6a-291b0c0790f8', 'date': 'Mon, 08 Jul 2019 22:11:56 GMT', 'content-type': 'text/xml', 'content-length': '432'}, 'RetryAttempts': 0}}"

    assert response == expected_response