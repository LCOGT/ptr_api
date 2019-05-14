# app.py

from endpoints import status, commands, data, sites
from flask import Flask, request, jsonify
import json, boto3, time
import auth
from flask_restplus import Api, Resource, fields
from flask_cors import CORS


application = Flask(__name__)
api = Api(app=application)
#cors = CORS(application, resources={r"/*": {"origins": "*"}})

#api = flaskrestful.namespace('photonranch', description="Communicate between photon ranch observatories and their clients.")

model = api.schema_model('Status', {
    'required': ['address'],
    'properties': {
        'mnt<id>_air': {
            'type': 'number',
            'description': 'Airmass of current pointing.'
        },
        'foc<id>_foc_moving': {
            'type': 'string',
            'description': 'True or False'
        },
        'etc...': {
        }
    },
    'type': 'object'
})

#-----------------------------------------------------------------------------#

@application.route('/home', methods=['GET', 'POST'])
def slash():
    return "flask api home page"

#-----------------------------------------------------------------------------#

# Site Status
@api.route('/<string:site>/status/')
class Status(Resource):

    @auth.required
    def get(self, site):
        """
        Get the latest general site status.
        """
        return status.get_status(site)

    @auth.required
    @api.expect(model, envelope='resource')
    def put(self, site):
        """ 
        Update a site's status. Requires observatory credentials.
        """
        return status.put_status(site)

#-----------------------------------------------------------------------------#

# Site Weather
@api.route('/<string:site>/weather/')
class Weather(Resource):

    def get(self, site):
        """
        Get the latest weather at a site.
        """
        return status.get_weather(site)

    @auth.required
    def put(self, site):
        """ 
        Update a site's current weather. Requires observatory credentials.
        """
        return status.put_weather(site)

#-----------------------------------------------------------------------------#

# Command Queue
@api.route('/<string:site>/<string:mount>/command/')
class Command(Resource):

    @auth.required
    def get(self, site, mount):
        """
        Get the oldest queued command to execute. Authorization required.
        """
        return commands.get_command(site, mount)

    @auth.required
    #@api.expect(model)
    def post(self, site, mount):
        """
        Send a command to the observatory command queue. Authorization required.
        """
        return commands.post_command(site, mount)

#-----------------------------------------------------------------------------#

# Uploads to S3
@api.route('/<string:site>/upload/')
class Upload(Resource):
    """ 
    A request for a presigned post url requires the name of the object
    and the path at which it is stored. This is sent in a single string under
    the key 'object_name' in the json-string body of the request.

    Example request body:
    '{"object_name":"raw_data/2019/image001.fits"}'

    This request will save an image into the main s3 bucket as:
    MAIN_BUCKET_NAME/site/raw_data/2019/img001.fits

    * * *

    Here's how another Python program can use the presigned URL to upload a file:

    with open(object_name, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    # If successful, returns HTTP status code 204
    logging.info(f'File upload HTTP status code: {http_response.status_code}')

    """

    @auth.required
    def get(self, site):
        return data.upload(site)

#-----------------------------------------------------------------------------#

# Site Configurations
@api.route('/<string:site>/config/')
class Config(Resource):

    def get(self, site):
        return sites.get_config(site)

    @auth.required
    def put(self, site):
        return sites.put_config(site)

        

