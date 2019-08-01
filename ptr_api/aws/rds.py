# aws/rds.py

import boto3
import psycopg2

REGION = "us-east-1"
URL_EXPIRATION = 3600 # Seconds until URL expiration

rds_c = boto3.client('rds', REGION)


def get_last_modified(cursor, connection, k):
    sql = "SELECT image_root FROM images ORDER BY capture_date DESC LIMIT %d" % k
    try:
        cursor.execute(sql)
        images = cursor.fetchmany(k)
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    return images
