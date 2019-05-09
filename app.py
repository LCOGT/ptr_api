# app2.py

from endpoints import status, commands, data, sites
from flask import Flask, request, jsonify
import json, boto3, time
import auth


application = Flask(__name__)


#-----------------------------------------------------------------------------#

@application.route('/', methods=['GET', 'POST'])
def slash():
    return jsonify({"result": "you've arrived at the home slash"})

#-----------------------------------------------------------------------------#

# Site Status
@application.route('/<site>/status/', methods=['GET'])
def get_status(site):
    return status.get_status(site)

@application.route('/<site>/status/', methods=['PUT'])
@auth.required
def put_status(site):
    return status.put_status(site)

#-----------------------------------------------------------------------------#

# Site Weather
@application.route('/<site>/weather/', methods=['GET'])
def get_weather(site):
    return status.get_weather(site)

@application.route('/<site>/weather/', methods=['PUT'])
@auth.required
def put_weather(site):
    return status.put_weather(site)

#-----------------------------------------------------------------------------#

# Command Queue
@application.route('/<site>/command/', methods=['GET'])
@auth.required
def get_command(site):
    return commands.get_command(site)

@application.route('/<site>/command/', methods=['POST'])
@auth.required
def post_command(site):
    return commands.post_command(site)

#-----------------------------------------------------------------------------#

# Uploads to S3
@application.route('/<site>/upload/', methods=['GET', 'POST'])
@auth.required
def upload(site):
    return data.upload(site)

#-----------------------------------------------------------------------------#

# Site Configurations
@application.route('/<site>/config/', methods=['GET'])
def get_config(site):
    return sites.get_config(site)

@application.route('/<site>/config/', methods=['PUT'])
@auth.required
def put_config(site):
    return sites.put_config(site)

        

