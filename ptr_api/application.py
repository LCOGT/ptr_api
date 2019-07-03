# app.py

#-----------------------------------------------------------------------------#

# TODO: any request for /some-new-site/status creates a new dynamodb table for
# 'some-new-site'. This could easily get out of hand.

# TODO: sites can post as any observatory by modifying the site name in the url.
# Ensure credentials only enable sending data from a single identity. 
#     note: maybe this doesn't matter since it's just program access anyways.

# TODO: change the presigned post url to be more strict about the save
# directory. Require inputs to specify what's being saved (eg. recent jpg) 
# and automatically provide the appropriate directory in the url. 

# TODO: make configuration easier to understand. Get the format of config json
# from Wayne if necessary. 

# TODO: distinguish observatory credentials from user credentials.




# OPTION: Currently, site status and weather are stored in the same dynamodb
# table. History is not preserved. Keep like this, or make separate weather
# and status tables with history from date-indexed elements?

# Testing a new git workflow.

#-----------------------------------------------------------------------------#

from ptr_api.endpoints import status, commands, data, sites
from flask import Flask, request, jsonify
import json, boto3, time
import ptr_api.auth
from flask_restplus import Api, Resource, fields
from flask_cors import CORS

application = Flask(__name__)
api = Api(app=application)
cors = CORS(application, resources={r"/*": {"origins": "*"}})

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

# API Homepage
class Home(Resource):

    def get(self):
        return {'about':'Flask API home page'}

#-----------------------------------------------------------------------------#

# Site Status
class Status(Resource):

    def get(self, site):
        '''
        Get the latest general site status. Requires observatory credentials.
        '''
        return status.get_status(site)

    @ptr_api.auth.required
    @api.expect(model, envelope='resource')
    def put(self, site):
        ''' 
        Update a site's status. Requires observatory credentials.
        '''
        return status.put_status(site)

#-----------------------------------------------------------------------------#

# Site Weather
class Weather(Resource):

    def get(self, site):
        '''
        Get the latest weather at a site.
        '''
        return status.get_weather(site)

    @ptr_api.auth.required
    def put(self, site):
        '''
        Update a site's current weather. Requires observatory credentials.
        '''
        return status.put_weather(site)

#-----------------------------------------------------------------------------#

# Command Queue
class Command(Resource):

    @ptr_api.auth.required
    def get(self, site, mount):
        '''
        Get the oldest queued command to execute. Authorization required.
        '''
        return commands.get_command(site, mount)

    @ptr_api.auth.required
    #@api.expect(model)
    def post(self, site, mount):
        '''
        Send a command to the observatory command queue. Authorization required.
        '''
        return commands.post_command(site, mount)

    def options(self, site, mount):
        print('inside options')
        return {'Allow' : 'POST,GET' }, 200, \
        { 'Access-Control-Allow-Origin': '*', \
        'Access-Control-Allow-Methods' : 'POST,GET', \
        'Access-Control-Allow-Headers': '*' }

#-----------------------------------------------------------------------------#

# Uploads to S3
class Upload(Resource):

    @ptr_api.auth.required
    def get(self, site):
        ''' 
        A request for a presigned post url, which requires the name of the object
        and the path at which it is stored. This is sent in a single string under
        the key 'object_name' in the json-string body of the request.

        Example request body:
        '{"object_name":"raw_data/2019/image001.fits"}'

        This request will save an image into the main s3 bucket as:
        <bucket_name>/site/raw_data/2019/img001.fits

        * * *

        Here's how another Python program can use the presigned URL to upload a file:

        with open(object_name, 'rb') as f:
            files = {'file': (object_name, f)}
            http_response = requests.post(response['url'], data=response['fields'], files=files)
        logging.info(f'File upload HTTP status code: {http_response.status_code}')

        '''
        return data.upload(site)

# Downloads from S3
class Download(Resource):

    def post(self, site):
        '''
        Get a link to download the specified s3 file.

        JSON body should include {"object_name": "path/to/file"} where the 
        path to the file starts inside the main site directory (so using the 
        path "site1/path/to/file" would be wrong).
        
        The path is specified as a url parameter.
        '''
        return data.download(site)

#-----------------------------------------------------------------------------#

# Site Configurations
class Config(Resource):

    def get(self, site):
        ''' 
        See the saved configuration of the specified site. 
        '''
        return sites.get_config(site)

    @ptr_api.auth.required
    def put(self, site):
        ''' 
        Set the configuration for a site.

        If the configuration has changed since the last entry, additional aws
        resources will be created as appropriate. 

        Note: if a configuration has changed, it must be updated here before
        continuing with any other action. 
        '''
        return sites.put_config(site)

class AllConfig(Resource):

    def get(self):
        '''
        Get all entries in the config table. 
        '''
        return sites.get_all_config()
        
#-----------------------------------------------------------------------------#

# Add resources to the API and define their routes
api.add_resource(Home, '/')
api.add_resource(Status,'/<string:site>/status/')
api.add_resource(Weather,'/<string:site>/weather/')
api.add_resource(Command,'/<string:site>/<string:mount>/command/')
api.add_resource(Upload,'/<string:site>/upload/')
api.add_resource(Download,'/<string:site>/download/')
api.add_resource(Config,'/<string:site>/config/')
api.add_resource(AllConfig,'/all/config/')


