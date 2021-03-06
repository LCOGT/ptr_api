# endpoints/site_config.py

from flask import jsonify, request
from ptr_api.aws import s3, sqs, dynamodb
import json


def get_config(site):
    ''' Used in application.Config.get '''
    # Get the dynamodb table that stores configurations for all sites.
    # Entries are identified by the k:v pair where k="site", v="<sitename>".
    key = {"site":site}
    config = dynamodb.get_item('site_configurations', key)
    return jsonify(config)


def put_config(site):
    ''' Used in application.Config.put '''

    # Receive the JSON config sent in the request.
    config_dict = json.loads(request.get_data())

    url_site = site
    config_site = config_dict['site']

    # Make sure the site in the config file matches the site in the url.
    if url_site != config_site:
        error = f"config site name ({config_site}) does not match site in "\
            f"url ({site})!"
        return jsonify({"ERROR": error})

    # Set the primary key. Used for retrieval.
    config = {
        "site": site,
        "configuration": config_dict
    }
    response = dynamodb.insert_item('site_configurations', config)

    # Ensure that all resources exist.
    init_from_config(site, config_dict)

    return jsonify(response)

def remove_site_resources(site):
    ''' Used in application.Config.delete '''
    # First, use the config to delete all site resources
    delete_from_config(site)

    # Finally, remove the config itself.
    key = {"site": site}
    response = dynamodb.delete_item("site_configurations", key)
    return response



# Parse a site configuration, create any resources that don't currently exist.
def init_from_config(site, config=None):
    if config is None:
        # Get the config for a site from the global config store
        key = {"site": site}
        config_dict = dynamodb.get_item('site_configurations', key)
        config = config_dict["configuration"]
        
    # SQS queue creation, one queue per mount
    site_mounts = config.get('mount', {}).keys()
    for mount in site_mounts:
        queue_name = f"{site}_{mount}.fifo"
        sqs.create_queue(queue_name)

    # Create a dynamodb table for the site (status and weather). Does nothing 
    # if it already exists.
    table_name = str(site)
    dynamodb.create_table(table_name)

    # Create a dynamodb table to track data from each site. Does nothing if
    # it already exists.
    #image_dynamodb_name = f"{site}_images"
    #dynamodb.create_table(image_dynamodb_name)

# Remove AWS resources for a given site, based on the site's configuration.
def delete_from_config(site, config=None):
    
    if config is None:
        # Get the config for a site from the global config store
        key = {"site": site}
        config_dict = dynamodb.get_item('site_configurations', key)
        config = config_dict["configuration"]

    # Remove SQS queues (one per mount). 
    site_mounts = config.get('mount', {}).keys()
    for mount in site_mounts: 
        queue_name = f"{site}_{mount}.fifo"
        sqs.delete_queue(queue_name, site)

    # Delete the dynamodb table used for storing status
    table_name = str(site)
    dynamodb.delete_table(table_name)
    

def get_all_config():
    return dynamodb.scan('site_configurations')
