# aws/dynamodb.py

import boto3, os, time
from botocore.exceptions import ClientError


REGION = os.environ.get('region')

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
        print(f"Successfully created dynamodb table: {table_name}")
    except: 
        try:
            response = dynamodb_c.describe_table(TableName=table_name)
            table = dynamodb_r.Table(table_name)
            print(f"Table did not create: table {table_name} already exists.")
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


def delete_item(table_name, key):
    ''' Delete an item from dynamodb. 
    @param key (dict): value is attribute name, val is attribute value.
    '''
    table = get_table(table_name)
    response = table.delete_item(Key=key)
    return response


def delete_table(table_name):
    ''' Delete a table from dynamodb
    Args:
        table_name (str): name of the table to delete
    Returns:
        True if table does not exist
        False if table still exists (due to some error)
    '''

    table_does_not_exist = False

    # Time to wait between attempts to delete a table that is in use.
    # Increments +5 seconds with each try.
    table_retry_delay = 0

    while not table_does_not_exist:
        table_retry_delay += 5

        # Try deleting the table
        try:
            table = get_table(table_name)
            response = table.delete()
            table_does_not_exist = True
            print(f"Successfully deleted table: {table_name}")

        # If there's a problem deleting the table
        except ClientError as e:

            # If no table exists, problem solved.
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f'Table not deleted: table {table_name} does not exist.')
                table_does_not_exist = True

            # If the table is in use, retry after a few seconds
            elif e.response['Error']['Code'] == 'ResourceInUseException':
                print(f'Table is currently in use and cannot be deleted. Retrying in {table_retry_delay} seconds...')
                time.sleep(table_retry_delay)
                continue

            # Some other error, will return False.
            else:
                print(f'Error deleting table {table_name}: ')
                print(e)
                break

    return table_does_not_exist


def scan(table_name):
    ''' return all items in the table in a list of dicts '''
    table = get_table(table_name)
    response = table.scan()
    items = {}
    for entry in response['Items']: 
        items[entry['site']] = entry['configuration']
    return items
