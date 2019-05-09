# aws/s3.py

import boto3
import os
from botocore.client import Config
from moto import mock_s3
from dotenv import load_dotenv
from os.path import join, dirname
from flask import jsonify

# Determine if we will run a local aws serice for testing.
load_dotenv('aws/.aws_config')
LOCAL_AWS = bool(int(os.environ.get('LOCAL_AWS')))
S3_PORT = int(os.environ.get('S3_PORT'))
BUCKET_NAME = str(os.environ.get('BUCKET_NAME'))
REGION = str(os.environ.get('REGION'))

def get_boto3_s3():

    # If we want a local mock s3:
    if LOCAL_AWS:
        s3_r = boto3.resource('s3', 
                               region_name=REGION,
                               config=Config(signature_version='s3v4'), 
                               endpoint_url=f'http://localhost:{S3_PORT}')
        s3_c = boto3.client('s3', 
                             region_name=REGION,
                             config=Config(signature_version='s3v4'), 
                             endpoint_url=f'http://localhost:{S3_PORT}')

    # If we want a real s3 instance: 
    else: 
        s3_r = boto3.resource('s3', REGION, config=Config(signature_version='s3v4'))
        s3_c = boto3.client('s3', REGION, config=Config(signature_version='s3v4'))
    return s3_r, s3_c


def get_image_url(site, filename):
    """
    Generate a publicly-accessible url to the image named <filename>.

    Files are saved to the provided site folder.
    """
    s3_r, s3_c = get_boto3_s3()

    params = {
        'Bucket': BUCKET_NAME,
        # Key = folder path + filename
        'Key': f'{site}/'+str(filename)
    }
    url = s3_c.generate_presigned_url(
        ClientMethod='get_object', 
        Params=params,
        ExpiresIn=3600 # URL expires in 1 hour.
    )
    return url

def get_presigned_post_url(bucket_name, object_name, 
                           fields=None, conditions=None, expiration=3600):
    """
    Here's how another Python program can use the presigned URL to upload a file:

    with open(object_name, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    # If successful, returns HTTP status code 204
    logging.info(f'File upload HTTP status code: {http_response.status_code}')

    """
    s3_r, s3_c = get_boto3_s3()

    try:
        response = s3_c.generate_presigned_post(bucket_name,
                                                object_name,
                                                Fields=fields,
                                                Conditions=conditions,
                                                ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        return jsonify({'error': e})

    return jsonify(response)


'''
if __name__=='__main__':
    s = S3('main')
    dirpath = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(dirpath, 'data/base.jpg')
    destination = 'ccd_test2.jpg'
    s.upload_file(destination)
'''