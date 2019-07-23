from ptr_api.aws import s3, dynamodb
from flask import request, jsonify
import json, os


BUCKET_NAME = "photonranch-001"

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


def get_recent_image(site):
    table_name = f"{site}_images"
    table = dynamodb.get_table(table_name)
    response = table.scan()

    items = []
    for i in response['Items']:
        items.append((i, int(float(i['upload_time']))))

    url = ''
    filename = ''
    if len(items) != 0:
        items.sort(key=lambda x: x[1])
        latest_item = items[-1][0]
        object_name = latest_item['path']
        filename = latest_item['filename']
        url = s3.get_presigned_url(BUCKET_NAME, object_name)
    return json.dumps({"url": url, "filename": filename})

def get_k_recent_images(site, k=1):
    ''' Get the k most recent jpgs in a site's s3 directory.

    This implementation assumes that an s3 query will not return elements in sorted order,
    (which I've not verified), so it will fetch all the jpgs, sort them by last modified,
    and grab the k most recent ones. 
    
    TODO: implement some sort of caching so that s3 does not need to dump all of the files
    with each request.

    '''

    # List of jpgs returned from s3 contents query
    jpgs = []

    # Get all jpgs in S3
    for key in get_matching_s3_objects(bucket=BUCKET_NAME, prefix=site, suffix='.jpg'):
        jpgs.append(key)

    # Sort by date last modified.
    jpgs.sort(key=lambda x: x['LastModified'], reverse=True)

    latest_k_jpgs = []

    # Save the url, filename, and modification time.
    for i in range(k):
        if i > len(jpgs): break
        this_jpg = jpgs[i]
        path = this_jpg['Key']
        filename = path.split('/')[-1]
        url = s3.get_presigned_url(BUCKET_NAME, path)
        last_modified = str(this_jpg['LastModified'])
        jpg_properties = {
            "recency_order": i,
            "url": url,
            "filename": filename,
            "last_modified": last_modified,
            }
        latest_k_jpgs.append(jpg_properties)

    return json.dumps(latest_k_jpgs)
        
def get_text_files(site):
    files = []

    # Get all text files in S3
    for key in get_matching_s3_objects(bucket=BUCKET_NAME, prefix=site, suffix='.txt'):
        path = key['Key']
        url = s3.get_presigned_url(BUCKET_NAME, path)
        files.append(url)
        print(url)

    return json.dumps(files)

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
