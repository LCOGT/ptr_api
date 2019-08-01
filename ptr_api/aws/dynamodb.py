# aws/dynamodb.py

import boto3, time, os, json
from dotenv import load_dotenv
from os.path import join, dirname


# Determine if we will run a local aws serice for testing.
LOCAL_AWS = 0
REGION = 'us-east-1'

dynamodb_r = boto3.resource('dynamodb', REGION)
dynamodb_c = boto3.client('dynamodb', REGION)

def create_table(table_name, hash_name='Type', read_throughput=2, write_throughput=2):
    try:
        table = dynamodb_r.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': hash_name,
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': hash_name,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': read_throughput,
                'WriteCapacityUnits': write_throughput
            }
        )
    except: 
        try:
            response = dynamodb_c.describe_table(TableName=table_name)
            table = dynamodb_r.Table(table_name)
        except:
            print('There was an error creating the table ' + table_name)

    return table


def get_table(table_name):
    return dynamodb_r.Table(table_name) 


def insert_item(table_name, item):
    """
    Insert item into database.
    Item must be of type dict, and contain the primary key/value.
    """
    table = get_table(table_name)
    response = table.put_item(Item=item)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return True
    else:
        return False


def get_item(table_name, key):
    """
    Get an item from dynamodb.
    @param key: dict must contain primary key, and value of target entry.
    """
    table = get_table(table_name)
    response = table.get_item(Key=key)
    item = response['Item']
    return item

def scan(table_name):
    ''' return all items in the table in a list of dicts '''
    table = get_table(table_name)
    response = table.scan()
    items = {}
    for entry in response['Items']: 
        items[entry['site']] = entry['configuration']
    return items
