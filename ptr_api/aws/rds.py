# aws/rds.py

import boto3
import psycopg2
import datetime, time
from ptr_api.aws import s3
from ptr_api import config_init

params = config_init.config()
aws_params = params['aws']

REGION = aws_params['region']
BUCKET_NAME = aws_params['bucket']

rds_c = boto3.client('rds', REGION)


def get_last_modified(cursor, connection, k):
    sql = (
        "SELECT image_root FROM images "
        "WHERE capture_date is not null "
        "ORDER BY capture_date "
        "DESC LIMIT %s"
    )
    try:
        cursor.execute(sql, (k, ))
        images = [result[0] for result in cursor.fetchmany(k)]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    return images

def get_site_last_modified(cursor, connection, site, k):
    sql = (
        "SELECT image_root, capture_date, observer, right_ascension, declination, filter_used, exposure_time, airmass, e13_jpg_exists, e13_fits_exists "
        "FROM images "
        "WHERE site = %s "
        "AND capture_date is not null "
        "ORDER BY sort_date "
        "DESC LIMIT %s "
    )
    try:
        cursor.execute(sql, (site, k))
        db_query = cursor.fetchall()

    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)

    images = []
    for index, item in enumerate(db_query):
        jpg13_url = ''
        fits13_url = ''
        # Get urls to some of the images, if they exist
        if item[8]: 
            full_jpg13_path = f"{site}/raw_data/2019/{item[0]}-E13.jpg"
            jpg13_url = s3.get_presigned_url(BUCKET_NAME,full_jpg13_path)
        if item[9]:
            full_fits13_path = f"{site}/raw_data/2019/{item[0]}-E13.fits.bz2"
            fits13_url = s3.get_presigned_url(BUCKET_NAME,full_fits13_path)

        # Format the capture_date to a javascript-ready timestamp (eg. miliseconds)
        capture_date = item[1].timetuple()
        capture_timestamp_milis = 1000*int(time.mktime(capture_date))

        image = {
            "recency_order": index,
            "base_filename": item[0],
            "capture_date": capture_timestamp_milis,
            "observer": item[2],
            "right_ascension": item[3],
            "declination": item[4],
            "filter_used": item[5],
            "exposure_time": item[6],
            "airmass": item[7],
            "jpg13_url": jpg13_url,
            "fits13_url": fits13_url,
            "url": jpg13_url, # to use with old code while rewriting this function. temporary.
        }
        images.append(image)
    
    #images = [result for result in db_query]
    #print('\n'.join('{}: {}'.format(*k) for k in enumerate(images)))
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

    def images_by_user_query(cursor, user):
    sql = "SELECT image_root FROM images JOIN projects ON images.image_id = projects.image_id"
    try:
        cursor.execute(sql, (observer,))
        images = [result[0] for result in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images

        SELECT OrderNumber, TotalAmount, FirstName, LastName, City, Country
      FROM [Order] JOIN Customer
        ON [Order].CustomerId = Customer.Id