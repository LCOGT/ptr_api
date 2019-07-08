import pytest, re
from ptr_api.aws import dynamodb
import boto3, time, os, json
from moto import mock_dynamodb2

@mock_dynamodb2
def test_create_table():
    table_name = 'test_jackie'
    table = dynamodb.create_table(table_name)

    assert True

#def test_get_table():
#    return

#def test_insert_item():
#    return

#def test_get_item():
#    return

#def test_scan():
#    return

