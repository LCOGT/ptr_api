# aws/rds.py
# TODO: clean up api and make sure only the functions that are being used are kept
# also make sure to merge/pull
# make sure data/rds keep seperate logic and use image package where you can
# create header table in database and only store int
# rename functions where appropriate
import boto3, os, sys
import psycopg2
import datetime, time, re
from ptr_api.aws import s3

REGION = os.environ.get('region')
BUCKET_NAME = os.environ.get('bucket')

rds_c = boto3.client('rds', REGION)


def get_last_modified_by_site(cursor, connection, site, k):
    sql = (
        "SELECT image_id, base_filename, site, capture_date, sort_date, right_ascension, declination, "
        "ex01_fits_exists, ex13_fits_exists, ex13_jpg_exists, altitude, azimuth, filter_used, airmass, "
        "exposure_time, created_user "
        "FROM images "
        "WHERE site = %s "
        "AND capture_date is not null "
        "ORDER BY sort_date "
        "DESC LIMIT %s "
    )
    images = []
    try:
        cursor.execute(sql, (site, k))
        db_query = cursor.fetchall()
        images = generate_image_packages(db_query, cursor)

    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)

    return images

def images_by_date_range(cursor, start_date, end_date):
    '''
    NOTE: start and end times must be in timestamp format -> 2019-07-10 04:00:00
    '''
    sql = "SELECT base_filename FROM images WHERE capture_date BETWEEN %s AND %s"
    images = []
    try:
        cursor.execute(sql, (start_date, end_date,))
        images = [result[0] for result in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images


def get_image_records_by_user(cursor, username):
    
    sql = (
        "SELECT image_id, base_filename, site, capture_date, sort_date, right_ascension, declination, "
        "ex01_fits_exists, ex13_fits_exists, ex13_jpg_exists, altitude, azimuth, filter_used, airmass, "
        "exposure_time, created_user "

        "FROM images img "
        "INNER JOIN users usr "
        "ON usr.user_id = img.created_user "
        "WHERE usr.user_name = %s "
        "ORDER BY sort_date DESC "
    )

    images = []
    try:
        #start = time.time()
        #print(f"start time: {start}")
        cursor.execute(sql, (username,))
        #cexecute = time.time()
        #print(f"cursor executed: {cexecute-start}")
        db_query = cursor.fetchall()
        #cfetch = time.time()
        #print(f"cursor fetchall: {cfetch-cexecute}")
        images = generate_image_packages(db_query, cursor)
        #imagepackage = time.time()
        #print(f"generated image package: {imagepackage-cfetch}")
        #print(f"number of items: {len(images)}")
    except (Exception, psycopg2.Error) as error :
        print("Error while retrieving records:", error)
    
    return images

# This function generates image packages that contain all information from the images table.
def generate_image_packages(db_query, cursor):

    attributes = [
        'image_id',
        'base_filename',
        'site',
        'capture_date',
        'sort_date',
        'right_ascension',
        'declination',
        'ex01_fits_exists',
        'ex13_fits_exists',
        'ex13_jpg_exists',
        'altitude',
        'azimuth',
        'filter_used',
        'airmass',
        'exposure_time',
        'created_user'
        ]

    image_packages = []
    try:
        for index, record in enumerate(db_query):
            image_package = dict(zip(attributes, record))
            image_package.update({'recency_order': index})
            
            # Format the capture_date to a javascript-ready timestamp (eg. miliseconds)
            capture_date = image_package['capture_date'].timetuple()
            capture_timestamp_milis = 1000*int(time.mktime(capture_date))
            image_package['capture_date'] = capture_timestamp_milis

            # Format the sort_date to a javascript-ready timestamp (eg. miliseconds)
            sort_date = image_package['sort_date'].timetuple()
            sort_timestamp_milis = 1000*int(time.mktime(sort_date))
            image_package['sort_date'] = sort_timestamp_milis

            # Extract site and base_filename for image path construction
            base_filename = image_package['base_filename']
            site = image_package['site']

            jpg13_url = ''
            # Get urls to some of the images, if they exist
            if image_package['ex13_jpg_exists']: 
                full_jpg13_path = f"{site}/raw_data/2019/{base_filename}-EX13.jpg"
                jpg13_url = s3.get_presigned_url(BUCKET_NAME,full_jpg13_path)
            image_package.update({'jpg13_url': jpg13_url})

            image_packages.append(image_package)
    except AttributeError:
        print('There was an error in the image package generation process. Check that sttributes line up with query results.')

    return image_packages

