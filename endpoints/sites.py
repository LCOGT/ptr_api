# endpoints/site_config.py

from flask import jsonify, request
from aws import s3, sqs, dynamodb
import json


def get_config(site):
    # Get the dynamodb table that stores configurations for all sites.
    # Entries are identified by the k:v pair where k="site", v="<sitename>".
    key = {"site":site}
    config = dynamodb.get_item('site_configurations', key)
    return jsonify(config)


def put_config(site):

    # Receive the JSON config sent in the request.
    config_dict = json.loads(request.get_data())

    # Set the primary key. Used for retrieval.
    config = {
        "site": site,
        "configuration": json.dumps(config_dict)
    }
    response = dynamodb.insert_item('site_configurations', config)

    # Ensure that all resources exist.
    init_from_config(site, config["configuration"])

    return jsonify(response)


# Parse a site configuration, create any resources that don't currently exist.
def init_from_config(site, config=None):

    if config is None:
        # Get the config for a site from the global config store
        key = {"site": site}
        config_json = dynamodb.get_item('site_configurations', key)
        config_dict = json.loads(config_json)
        config = config_dict["configuration"]
    else:
        config = json.loads(config)

    # SQS queue creation, one queue per mount
    site_mounts = config['mounts'] # a list of string names
    for mount in site_mounts:
        queue_name = f"{site}_{mount}_queue.fifo"
        sqs.get_queue(queue_name)

    # Try creating the dynamodb table for the site. No action if it exists.
    table_name= str(site)
    dynamodb.get_table(table_name)