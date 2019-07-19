# client.py

# This class automates authentication token management and allows access to 
# the restricted api endpoints. 

# Running this file will test all api methods. 

import requests, os, json, time, random
from warrant import Cognito
from dotenv import load_dotenv
from os.path import join, dirname
from sample_message_bodies import *
import tkinter as tk


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

        self.user.authenticate(password=self.password)


    def base_url(self, port):
        local = f"http://localhost:{port}"
        eb = "http://api.photonranch.org"
        eb1 = "http://ptr-api.us-east-1.elasticbeanstalk.com"
        return local 


    def make_authenticated_header(self):
        header = {}
        try:
            self.user.check_token()
            header["Authorization"] = f"Bearer {self.user.access_token}"
        except AttributeError as e:
            print(e)
        return header


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

    # Test all Endpoints: Each item is one request
    endpoints = [
        {'uri': 'site1/config/', 'method': 'PUT', 'payload': sample_config},
        {'uri': 'site2/config/', 'method': 'PUT', 'payload': sample_config2},
        {'uri': 'site3/config/', 'method': 'PUT', 'payload': sample_config3},
        {'uri': 'site4/config/', 'method': 'PUT', 'payload': sample_config4},
        {'uri': 'site5/config/', 'method': 'PUT', 'payload': sample_config5},
        {'uri': 'site4/config/', 'method': 'PUT', 'payload': simple_config},

        {'uri': 'site1/status/', 'method': 'PUT', 'payload': site_status},
        {'uri': 'site1/weather/', 'method': 'PUT', 'payload': weather_status},

        {'uri': 'site1/mount1/command/', 'method': 'POST', 'payload': goto_cmd},

        {'uri': 'site1/status/', 'method': 'GET', 'payload': None},
        {'uri': 'site1/weather/', 'method': 'GET', 'payload': None},
        {'uri': 'site1/mount1/command/', 'method': 'GET', 'payload': None},
        {'uri': 'site1/config/', 'method': 'GET', 'payload': None},
        {'uri': 'site1/upload/', 'method': 'GET', 'payload': sample_upload_request},
        {'uri': 'site1/download/', 'method': 'POST', 'payload': sample_upload_request},
        {'uri': 'all/config/', 'method': 'GET', 'payload':None}
    ]

    # Create GUI for choosing endpoints to testing
    win = tk.Tk()
    win.title("PTR-API: Endpoint Tester")
    endpoint_vars = []

    def close_window(): 
        win.destroy()
    
    test_all_endpoints = tk.IntVar()
    tk.Checkbutton(win, text='Test All Endpoints', variable=test_all_endpoints).grid(row=1, sticky=tk.W)
    for e in range(len(endpoints)):
        endpoint_vars.append(tk.IntVar())
        endpoint_name = endpoints[e]['uri']+'\n'+'METHOD: '+endpoints[e]['method']
        tk.Checkbutton(win, text=endpoint_name, variable=endpoint_vars[e]).grid(row=e+2, sticky=tk.W)
    tk.Button(win, text='TEST', command=win.quit).grid(row=len(endpoints)+2, sticky=tk.W, pady=4)

    win.mainloop()
    
    # Test selected endpoints
    print('\n')
    print('TESTING ENDPOINTS:') # If endpoint was checked for testing, send request and print response
    print('********************************************************************************')
    responses = {}
    res = 'No responses'
    for i in range(len(endpoints)):
        if endpoint_vars[i].get()==1:
            e = endpoints[i]
            method = e['method']
            if method == 'GET':
                res = c.get(e['uri'], e['payload'])
            if method == 'POST':
                res = c.post(e['uri'], e['payload'])
            if method == 'PUT': 
                res = c.put(e['uri'], e['payload'])
            print('RESPONSE FROM: '+e['uri']+' USING HTTP METHOD: '+e['method'])
            print(json.dumps(res, indent=2)+'\n')
    print('********************************************************************************')
    print("Completed all api calls.")
    print('\n')

