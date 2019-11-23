# aws/sqs.py

import boto3, os, time
from botocore.exceptions import ClientError



REGION = os.environ.get('region')

sqs_r = boto3.resource('sqs', REGION)
sqs_c = boto3.client('sqs', REGION)

def create_queue(queue_name):
    ''' Note: unlike the 'create_table' function in dynamodb.py, this function 
    does not return a queue. I'm not sure why this was the original design 
    choice. Might want to improve this later. '''

    queue_attributes = {
        'FifoQueue': 'true',
        'DelaySeconds': '0',
        'MessageRetentionPeriod': '900', # 15 minutes to complete a command, else deleted.
        'ContentBasedDeduplication': 'true'
    }

    # First, check if the queue already exists
    try: 
        queue = sqs_r.get_queue_by_name(QueueName=queue_name)
        print(f"Queue already exists (did not create): {queue_name}")
        return

    # If the queue doesn't exist, try to create it.
    except:
        pass

    # Loop until the queue exists:
    queue_exists = False
    number_of_retries = 0
    while not queue_exists:

        try:
            queue = sqs_r.create_queue(QueueName=queue_name, Attributes=queue_attributes)
            print(f"Created queue: {queue_name}")
            queue_exists = True

        # Creation will fail if it was deleted in the last 60 seconds.
        # If this is the case, retry every few seconds until success.
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.QueueDeletedRecently':
                print('Recently deleted queues require 60 before creating another with the same name.')
                print('Retrying in 5 seconds...')
                number_of_retries += 1
                time.sleep(5)
            

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
        VisibilityTimeout=10, # This CANNOT BE 0!  
        WaitTimeSeconds=3 # 0==short polling, 0<x<20==long polling
    )
    try:
        message = response['Messages'][0]
        # receipt_handle is used to delete the entry from the queue.
        receipt_handle = message['ReceiptHandle']
        # print(f"{message['Body']} was received.\n")
        delete_response = sqs_c.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return message['Body']
    except KeyError as e:
        #print("No new messages.")
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

def delete_queue(queue_name, sitename=''):
    ''' Delete an SQS queue.

    Args:
        queue_name (str): name of the queue to delete
        sitename (str): site abbreviation used to filter the full list of queues. 
    Return:
        True or False
    '''

    queue_does_not_exist = False

    # Get all the queues. Optionally, filter by sitename prefix.
    queue_list = sqs_c.list_queues(
        QueueNamePrefix=sitename
    )

    # Check if the queue we want to delete exists
    for qurl in queue_list['QueueUrls']:

        # Get the name of the queue from its url 
        qname = qurl.split('/')[-1]
        if qname == queue_name:
            try: 
                response = sqs_c.delete_queue(QueueUrl=qurl)
                queue_does_not_exist = True
                print(f"Successfully deleted queue: {queue_name}")
                break

            except ClientError as e:
                if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    print(f"Queue did not delete: queue {queue_name} doesn't exist.")
                    queue_does_not_exist = True

                else:
                    print('Error while deleting queue: ')
                    print(e)

    return queue_does_not_exist

    
            
        

    #queue = sqs_r.get_queue_by_name(QueueName=queue_name)
    #try:
        #queue_url = queue.url
    #except Excption as e:
        #print(e)
        #print("Unable to delete queue: queue does not exist")
        #return
    #response = sqs_c.delete_queue(
        #QueueUrl=queue.url
    #)
    #return response
