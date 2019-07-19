# aws/sqs.py

import boto3
import os

REGION = 'us-east-1'

sqs_r = boto3.resource('sqs', REGION)
sqs_c = boto3.client('sqs', REGION)

def create_queue(queue_name):
    queue_attributes = {
        'FifoQueue': 'true',
        'DelaySeconds': '0',
        'MessageRetentionPeriod': '900', # 15 minutes to complete a command, else deleted.
        'ContentBasedDeduplication': 'true'
    }

    try: 
        queue = sqs_r.get_queue_by_name(QueueName=queue_name)
    except:
        queue = sqs_r.create_queue(QueueName=queue_name, Attributes=queue_attributes)


def list_all_queues(queue_name_prefix=''):
    all_queues = sqs_c.list_queues(QueueNamePrefix=queue_name_prefix)    
    print(all_queues['QueueUrls'])
    print(type(all_queues))


def get_queue_item(queue_name):
    """
    Read one entry in the queue. 
    If successful, return the message body and delete the entry in sqs.
    If unsuccessful (ie. queue is empty), return False.
    """

    queue = sqs_r.get_queue_by_name(QueueName=queue_name)
    queue_url = queue.url

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
    
    queue = sqs_r.get_queue_by_name(QueueName=queue_name)
    queue_url = queue.url

    # All messages with this group id will maintain FIFO ordering.
    messageGroupId = 'primary_message_group_id'

    response = sqs_c.send_message(
        QueueUrl=queue_url,
        MessageBody=messageBody,
        MessageGroupId=messageGroupId,
    )
    return response
    #print(f"Sent message. Message id is {response['MessageId']}")
