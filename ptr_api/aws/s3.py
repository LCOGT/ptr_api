# aws/s3.py

import boto3
import os
from botocore.client import Config
from moto import mock_s3
from dotenv import load_dotenv
from os.path import join, dirname
from flask import Flask, jsonify

REGION = "us-east-1"

# docs: https://bit.ly/2Hqz7Bd
def get_presigned_url(bucket_name, object_name):
    """
    Generate a publicly-accessible url to the image named <filename>.

    Files are saved to the provided site folder.
    """
    s3_c = boto3.client('s3', REGION, config=Config(signature_version='s3v4'))

    params = {
        'Bucket': bucket_name,
        # Key = folder path + filename
        'Key': object_name,
    }
    try:
        url = s3_c.generate_presigned_url(
            ClientMethod='get_object', 
            Params=params,
            ExpiresIn=3600 # URL expires in 1 hour.
        )
    except Exception as e:
        print(f"error in generate_presigned_url: {e}")
    return url

# docs: https://bit.ly/2vYARfw 
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
    s3_c = boto3.client('s3', REGION, config=Config(signature_version='s3v4'))

    try:
        response = s3_c.generate_presigned_post(bucket_name,
                                                object_name,
                                                Fields=fields,
                                                Conditions=conditions,
                                                ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        return jsonify({'error': e})

    print(jsonify(response))
    return jsonify(response)


'''
if __name__=='__main__':
    s = S3('main')
    dirpath = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(dirpath, 'data/base.jpg')
    destination = 'ccd_test2.jpg'
    s.upload_file(destination)
'''