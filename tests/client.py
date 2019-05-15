# client.py

# This class automates authentication token management and allows access to 
# the restricted api endpoints. 

# Running this file will test all api methods. 

import requests, os, json, time, random
from warrant import Cognito
from dotenv import load_dotenv
from os.path import join, dirname

# Determine if we will run a local aws serice for testing.
load_dotenv('aws/.aws_config')
LOCAL_AWS = bool(int(os.environ.get('LOCAL_AWS')))

class Client:

    def __init__(self): 

        # AWS cognito account info imported from .env
        dotenv_path = join(dirname(__file__), '.client_env')
        load_dotenv(dotenv_path)
        self.region = os.environ.get('client_REGION')
        self.userpool_id = os.environ.get('client_USERPOOL_ID')
        self.app_id_client = os.environ.get('client_APP_CLIENT_ID')
        self.app_client_secret = os.environ.get('client_APP_CLIENT_SECRET')
        self.username = os.environ.get('client_USERNAME')
        self.password = os.environ.get('client_PASS')

        self.user = Cognito(self.userpool_id, 
                       self.app_id_client, 
                       client_secret=self.app_client_secret, 
                       username=self.username,
                       user_pool_region=self.region)

        # This is only important if we're not on a local mock server.
        if LOCAL_AWS is False:
            try:
                self.user.authenticate(password=self.password)
            except Exception as e:
                print(f"error: {e}")

    def base_url(self, port):
        local = f"http://localhost:{port}"
        eb = "http://api.photonranch.org"
        return local


    def make_authenticated_header(self):
        header = {}
        if LOCAL_AWS is False:
            try:
                self.user.check_token()
                header["Authorization"] = f"Bearer {self.user.access_token}"
            except AttributeError as e:
                print(e)
        return header



    def public_api_route(self):
        response = requests.get("http://localhost:5000/public")
        return response.text


    def private_api_route(self):
        header = self.make_authenticated_header()
        response = requests.get("http://localhost:5000/private", headers=header) 
        return response.text

    def get(self, uri, payload=None, port=5000):
        header = self.make_authenticated_header()
        if payload is None:
            response = requests.get(f"{self.base_url(port)}/{uri}", headers=header) 
        else:
            response = requests.get(f"{self.base_url(port)}/{uri}", data=json.dumps(payload), headers=header)
        return response.json()

    def put(self, uri, payload, port=5000):
        ''' Localhost put request at the specified uri and access token.

        Args: 
            uri (str): the part of the url after the port. Eg: 'site1/status/'.
            payload (dict): body that will be converted to a json string. 
            port (int): optional, specifies localhost port. 

        Return: 
            json response from the request.
        '''

        header = self.make_authenticated_header()
        response = requests.put(f"{self.base_url(port)}/{uri}", data=json.dumps(payload), headers=header) 
        return response.json()

    def post(self, uri, payload, port=5000):
        ''' Localhost post request at the specified uri and access token.

        Args: 
            uri (str): the part of the url after the port. Eg: 'site1/status/'.
            payload (dict): body that will be converted to a json string. 
            port (int): optional, specifies localhost port. 

        Return: 
            json response from the request.
        '''

        header = self.make_authenticated_header()
        response = requests.post(f"{self.base_url(port)}/{uri}", data=json.dumps(payload), headers=header) 
        return response.json()



if __name__=="__main__":
    c = Client()

    ### Test all endpoints ###

    # Sample message bodies. 
    site_status = {
        "parked": "True", 
        "timestamp": str(int(time.time()))
    }
    weather_status = {
        "wind": "blowing", 
        "rain": "no", 
        "timestamp": str(int(time.time()))
    }
    goto_cmd = {
        "device": "mount_1",
        "ra": random.randint(0,24),
        "dec": random.randint(-90,90),
        "command": "goto",
        "timestamp": str(int(time.time()))
    } 
    sample_config = {
        "site": "site1",
        "mounts": [
            "mount1", "mount2"#, "mount3"
        ]
    }
    sample_upload_request = {
        "object_name": "raw_data/2019/a_file.txt"
    }

    # Each item is one request
    endpoints = [
        {'uri': 'site1/config/', 'method': 'PUT', 'payload': sample_config},
        #{'uri': 'site1/status/', 'method': 'PUT', 'payload': site_status},
        #{'uri': 'site1/weather/', 'method': 'PUT', 'payload': weather_status},

        #{'uri': 'site1/mount1/command/', 'method': 'POST', 'payload': goto_cmd},

        #{'uri': 'site1/status/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/weather/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/mount1/command/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/config/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/upload/', 'method': 'GET', 'payload': sample_upload_request},
    ]

    responses = {}
    for e in endpoints:
        method = e['method']
        if method == 'GET':
            res = c.get(e['uri'], e['payload'])
        if method == 'POST':
            res = c.post(e['uri'], e['payload'])
        if method == 'PUT': 
            res = c.put(e['uri'], e['payload'])
        responses[f"{e['uri']}:{e['method']}"] = res
    
            
    # Print all the responses from each endpoint in formatted json. 
    print(json.dumps(responses, indent=2))
    print("Completed all api calls.")


    # Upload a file using the presigned post link
    if False:
        upload_response = responses['site1/upload/:GET']
        object_name = 'init_resources.py'
        with open('aws/init_resources.py', 'rb') as f:
            files = {'file': (object_name, f)}
            http_response = requests.post(upload_response['url'], data=upload_response['fields'], files=files)
        print(f'File upload HTTP status code: {http_response.status_code}')

    # Get a link to download the file just uploaded.
    if False: 
        body = {"object_name": "raw_data/2019/a_file.txt"}
        print(c.get('site1/download/', body))