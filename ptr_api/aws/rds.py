# aws/rds.py

import boto3
import psycopg2
from ptr_api import config_init

params = config_init.config()
aws_params = params['aws']

REGION = aws_params['region']

rds_c = boto3.client('rds', REGION)


def get_last_modified(cursor, connection, k):
    sql = "SELECT image_root FROM images ORDER BY capture_date DESC LIMIT %s"
    try:
        cursor.execute(sql, (k, ))
        images = [result[0] for result in cursor.fetchmany(k)]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    return images
  
def images_by_site_query(cursor, site):
    sql = "SELECT image_root FROM images WHERE site = %s"
    try:
        cursor.execute(sql, (site,))
        images = [result[0] for result in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images

def images_by_observer_query(cursor, observer):
    sql = "SELECT image_root FROM images WHERE observer = %s"
    print(observer)
    try:
        cursor.execute(sql, (observer,))
        images = [result[0] for result in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images

def images_by_date_range_query(cursor, start_date, end_date):
    '''
    NOTE: start and end times must be in timestamp format -> 2019-07-10 04:00:00
    '''
    sql = "SELECT image_root FROM images WHERE capture_date BETWEEN %s AND %s"
    try:
        cursor.execute(sql, (start_date, end_date,))
        images = [result[0] for result in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images