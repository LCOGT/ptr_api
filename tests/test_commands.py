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
    