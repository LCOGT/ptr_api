# aws/sqs.py

import boto3
import sys,time,random,json, subprocess, os
from moto import mock_sqs
from dotenv import load_dotenv
from os.path import join, dirname

# Determine if we will run a local aws serice for testing.
load_dotenv('aws/.aws_config')
LOCAL_AWS = bool(int(os.environ.get('LOCAL_AWS')))
SQS_PORT = int(os.environ.get('SQS_PORT'))
REGION = str(os.environ.get('REGION'))


def get_boto3_sqs():
    # If we want a local mock queue:
    if LOCAL_AWS:
        sqs_r = boto3.resource('sqs', region_name=REGION, endpoint_url=f'http://localhost:{SQS_PORT}')
        sqs_c = boto3.client('sqs', region_name=REGION, endpoint_url=f'http://localhost:{SQS_PORT}')
    # If we want a real sqs instance: 
    else: 
        sqs_r = boto3.resource('sqs', REGION)
        sqs_c = boto3.client('sqs', REGION)
    return sqs_r, sqs_c

def get_queue(queue_name):

    queue_attributes = {
        'FifoQueue': 'true',
        'DelaySeconds': '0',
        'MessageRetentionPeriod': '900', # 15 minutes to complete a command, else deleted.
        'ContentBasedDeduplication': 'true'
    }

    sqs_r, sqs_c = get_boto3_sqs()

    queue = sqs_r.get_queue_by_name(QueueName=queue_name)

    return queue.url, sqs_r, sqs_c

def create_queue(queue_name):

    queue_attributes = {
        'FifoQueue': 'true',
        'DelaySeconds': '0',
        'MessageRetentionPeriod': '900', # 15 minutes to complete a command, else deleted.
        'ContentBasedDeduplication': 'true'
    }

    sqs_r, sqs_c = get_boto3_sqs()

    try: 
        queue = sqs_r.get_queue_by_name(QueueName=queue_name)
    except:
        queue = sqs_r.create_queue(QueueName=queue_name, Attributes=queue_attributes)

    return queue.url, sqs_r, sqs_c

def list_all_queues(queue_name_prefix=''):
    sqs_r, sqs_c = get_boto3_sqs()
    all_queues = sqs_c.list_queues(QueueNamePrefix=queue_name_prefix)    
    print(all_queues['QueueUrls'])
    print(type(all_queues))


def get_queue_item(queue_name):
    """
    Read one entry in the queue. 
    If successful, return the message body and delete the entry in sqs.
    If unsuccessful (ie. queue is empty), return False.
    """

    queue_url, sqs_r, sqs_c = get_queue(queue_name)

    response = sqs_c.receive_message(
        QueueUrl=queue_url,
        #AttributeNames=[ 'device' ],
        MaxNumberOfMessages=1,    
        #MessageAttributeNames=[ 'All' ],
        VisibilityTimeout=10,         #This CANNOT BE 0!  
        WaitTimeSeconds=3 # 0==short polling, 0<x<20==long polling
    )
    try:
        message = response['Messages'][0]
        # receipt_handle is used to delete the entry from the queue.
        receipt_handle = message['ReceiptHandle']
        # print(f"{message['Body']} was received.\n")
        delete_response = sqs_c.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return message['Body']
    except Exception as e:
        print("error in get_queue_item: ")
        print(e)
        return False

def send_to_queue(queue_name, messageBody="empty body"):
    """
    Send a message to the 'toAWS' queue.
    Args:
        messagebody (str): body of the message to send.
    """

    queue_url, sqs_r, sqs_c = get_queue(queue_name)

    # All messages with this group id will maintain FIFO ordering.
    messageGroupId = 'primary_message_group_id'

    print(f'message body (from sqs module): {messageBody}')

    response = sqs_c.send_message(
        QueueUrl=queue_url,
        MessageBody=messageBody,
        MessageGroupId=messageGroupId,
    )
    return response
    #print(f"Sent message. Message id is {response['MessageId']}")
