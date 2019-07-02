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
    A request for a presigned post url requires the name of the object
    and the path at which it is stored. This is sent in a single string under
    the key 'object_name' in the json-string body of the request.

    Example request body:
    '{"object_name":"raw_data/2019/a_file.txt"}'

    This request will save an image into the main s3 bucket as:
    MAIN_BUCKET_NAME/site/raw_data/2019/img001.fits
    
    * * *

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
