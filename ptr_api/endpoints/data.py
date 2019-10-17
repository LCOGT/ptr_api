from ptr_api.aws import s3, dynamodb, rds
from flask import request, jsonify
import json, os, time
import psycopg2


BUCKET_NAME = os.environ.get('bucket')
CONNECTION_PARAMETERS = {
    'host': os.environ['host'],
    'database': os.environ['database'],
    'user': os.environ['user'],
    'password': os.environ['password']
}

def upload(site):
    content = json.loads(request.get_data())
    object_name = f"{site}/{content['object_name']}"
    response = s3.get_presigned_post_url(BUCKET_NAME, object_name)
    return jsonify(response)


def download(site):
    content = json.loads(request.get_data())
    object_name = f"{site}/{content['object_name']}"
    url = s3.get_presigned_url(BUCKET_NAME, object_name)
    return url

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

import boto3
# Code from https://alexwlchan.net/2018/01/listing-s3-keys-redux/
def get_matching_s3_objects(bucket, prefix='', suffix=''):
    """
    Generate objects in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)

        try:
            contents = resp['Contents']
        except KeyError:
            return

        for obj in contents:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield obj

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj['Key']

def get_k_recent_images(site, k=1):
    ''' 
    Get the k most recent jpgs in a site's s3 directory.
    '''
    connection = None
    try:
        connection = psycopg2.connect(**CONNECTION_PARAMETERS)
        cursor = connection.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Connection to database failed.")
        print(error)
        return json.dumps([])
        
    # List of k last modified files returned from ptr archive query
    latest_k_files = rds.get_last_modified_by_site(cursor, connection, site, k)

    if connection is not None:
        connection.close()

    return json.dumps(latest_k_files)


def get_filtered_images():
    '''
    NOTE: dates must be in UTC timestamp format -> 2019-07-10 04:00:00
    '''
    filter_params = request.args.to_dict()
    connection = None
    try:
        connection = psycopg2.connect(**CONNECTION_PARAMETERS)
        cursor = connection.cursor()

        #retrieve images with given filter parameters
        images = rds.filtered_images(cursor, filter_params)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
    
    return images


def get_images_by_user(username):
    ''' Retrieve all images taken by a user, and return metadata + urls. '''
    images = []
    connection = None
    try:
        connection = psycopg2.connect(**CONNECTION_PARAMETERS)
        cursor = connection.cursor()
        images = rds.get_image_records_by_user(cursor, username)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if connection is not None:
            connection.close()
    return json.dumps(images)

    
def get_fits13_url(site, base_filename):
    full_fits13_path = f"{site}/raw_data/2019/{base_filename}-EX13.fits.bz2"
    return s3.get_presigned_url(BUCKET_NAME,full_fits13_path)
            
def get_fits01_url(site, base_filename):
    full_fits01_path = f"{site}/raw_data/2019/{base_filename}-EX01.fits.bz2"
    return s3.get_presigned_url(BUCKET_NAME,full_fits01_path)