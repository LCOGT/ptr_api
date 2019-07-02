from flask import request, jsonify
import json, os
from ptr_api.aws import s3

BUCKET_NAME = str(os.environ.get('BUCKET_NAME'))

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
