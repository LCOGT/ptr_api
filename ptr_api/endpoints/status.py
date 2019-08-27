# endpoints.py

# This is the source of the functions that run at each endpoint in the app.
# The purpose is to maximize code readability for myself. 
# The structure (but not function content) will likely change again anyways. 

from flask import request, jsonify
import json
from ptr_api.aws import dynamodb


def get_status(site):
    """ Return the status of the requested site in JSON

    This is a public endpoint. 

    Args:
        site (string): Site name embedded in this requests url.
    
    Returns (json): site status
    """
        
    table_name = str(site)

    # The value of the status key specifies what state to get.
    key = {"Type":"State"}

    status = dynamodb.get_item(table_name, key)
    return jsonify({
        "site": site, 
        "content": status
        })

def put_status(site):
    """ Update site status, used by observatories only.

    Private endpoint; requires a valid access-JWT in the request header.

    Args:
        site (string): Site name embedded in this requests url.
        PUT data (json): dict converted to json with all status information.
    """

    # Load the body of the request (json string) into a python dictionary.
    content = json.loads(request.get_data())
    content["Type"] = "State"
    table_name = str(site)

    response = dynamodb.insert_item(table_name, content)
    return jsonify({
        "result": site,
        "method": "PUT",
        "content": "status"
        })

#-----------------------------------------------------------------------------#

def get_weather(site):
    table_name = str(site)
    key = {"Type":"Weather"}

    status = dynamodb.get_item(table_name, key)
    return jsonify({
        "site": site, 
        "method": "GET",
        "content": status 
        })

def put_weather(site):
    # Load the body of the request (json string) into a python dictionary.
    content = json.loads(request.get_data())
    content["Type"] = 'Weather' # It might be wise to check this instead of setting it.
    table_name = str(site)

    response = dynamodb.insert_item(table_name, content)
    return jsonify({
        "result": site, 
        "method": "PUT",
        "content": "weather"
        })
