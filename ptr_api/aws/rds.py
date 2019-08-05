# aws/rds.py

import boto3
import psycopg2
from ptr_api import config_init

params = config_init.config()
aws_params = params['aws']

REGION = aws_params['region']

rds_c = boto3.client('rds', REGION)


def get_last_modified(cursor, connection, k):
    sql = "SELECT image_root FROM images ORDER BY capture_date DESC LIMIT %d" % k
    try:
        cursor.execute(sql)
        images = cursor.fetchmany(k)
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    return images
  
