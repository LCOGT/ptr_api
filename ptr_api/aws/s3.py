# aws/s3.py

import boto3
from botocore.client import Config
from cachetools import cached, TTLCache
from ptr_api import config_init

params = config_init.config()
aws_params = params['aws']
REGION = aws_params['region']

s3_put_ttl = 300  # This is how long the post url is valid
s3_get_ttl = 3600 # This is how long a get url is valid

s3_c = boto3.client('s3', REGION, config=Config(signature_version='s3v4'))


# docs: https://bit.ly/2Hqz7Bd
@cached( cache=TTLCache(maxsize=1024, ttl=(0.9*s3_get_ttl)) )
def get_presigned_url(bucket_name, object_name):
    """
    Generate a publicly-accessible url to the specified image.
    Since the url strings change each second (due to the expiration time encoding),
    we cache the results of a given image for the length of its lifetime. Previously,
    the browser would recieve a different url with each request to the same image, 
    but now it is able to cache the results for the ttl duration.

    Note: generating presigned urls does not require an internet connection.

    """
    params = {
        'Bucket': bucket_name,
        'Key': object_name, # Key = folder path + filename
    }
    try:
        url = s3_c.generate_presigned_url(
            ClientMethod='get_object', 
            Params=params,
            ExpiresIn=s3_get_ttl 
        )
    except Exception as e:
        print(f"error in generate_presigned_url: {e}")
        
    return url


# docs: https://bit.ly/2vYARfw 
def get_presigned_post_url(bucket_name, object_name):
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
        
    If successful, returns HTTP status code 204
    logging.info(f'File upload HTTP status code: {http_response.status_code}')

    """

    try:
        response = s3_c.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            ExpiresIn=URL_EXPIRATION 
        )
    except ClientError as e:
        print(e)
        return {'error': e}

    return response
