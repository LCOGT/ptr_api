from ptr_api import environment
import pytest
import boto3
import os, random
from ptr_api.aws import dynamodb

@pytest.fixture
def dynamodb_mocker(scope='session', autouse=True):
    dynamodb_r_mock = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url=f'http://localhost:5003')
    dynamodb_c_mock = boto3.client('dynamodb', region_name='us-east-1', endpoint_url=f'http://localhost:5003')
    
    table_name = f"{random.randint(0,100000)}_tablename"

    table = dynamodb_r_mock.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'Test_Attribute',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Type',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 2,
            'WriteCapacityUnits': 2
        }
    )

    yield (dynamodb_r_mock, dynamodb_c_mock, table, table_name)

def test_create_table(dynamodb_mocker):
    dynamodb_r_mock, dynamodb_c_mock, table, table_name = dynamodb_mocker

    test_table_name = f"{random.randint(0,100000)}_test_tablename"

    dynamodb.dynamodb_r = dynamodb_r_mock
    dynamodb.dynamodb_c = dynamodb_c_mock
    try:
        test_table = dynamodb.create_table(test_table_name)
    except:
        test_table = None

    assert test_table != None 

def test_insert_item(dynamodb_mocker):
    dynamodb_r_mock, dynamodb_c_mock, table, table_name = dynamodb_mocker

    test_item = {"Test_Attribute": "test"}

    dynamodb.dynamodb_r = dynamodb_r_mock
    dynamodb.dynamodb_c = dynamodb_c_mock
    result = dynamodb.insert_item(table_name, test_item)

    assert result

def test_get_item(dynamodb_mocker):
    dynamodb_r_mock, dynamodb_c_mock, table, table_name = dynamodb_mocker

    test_item = {"Test_Attribute": "test"}
    table.put_item(Item=test_item)

    dynamodb.dynamodb_r = dynamodb_r_mock
    dynamodb.dynamodb_c = dynamodb_c_mock
    item = dynamodb.get_item(table_name, test_item)
    assert item == test_item

