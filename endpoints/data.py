from flask import request, jsonify
import json, os
from aws import s3, dynamodb

BUCKET_NAME = str(os.environ.get('BUCKET_NAME'))

def upload(site):
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
    content = json.loads(request.get_data())
    object_name = f"{site}/{content['object_name']}"
    return s3.get_presigned_post_url(BUCKET_NAME, object_name)

def download(site):
    content = json.loads(request.get_data())
    object_name = f"{site}/{content['object_name']}"
    return s3.get_presigned_url(BUCKET_NAME, object_name)

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

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
