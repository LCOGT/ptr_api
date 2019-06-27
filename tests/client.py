# client.py

# This class automates authentication token management and allows access to 
# the restricted api endpoints. 

# Running this file will test all api methods. 

import requests, os, json, time, random
from warrant import Cognito
from dotenv import load_dotenv
from os.path import join, dirname

# Determine if we will run a local aws serice for testing.
dotenv_path_awsconfig = join(dirname(__file__),'../aws/.aws_config')
load_dotenv(dotenv_path_awsconfig)
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
        eb1 = "http://ptr-api.us-east-1.elasticbeanstalk.com"
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
        "mounts": {
            "mount1": {
                "telescopes": {}
            }, 
            "mount2": {
                "telescopes": {}
            }, 
            "mount3": {
                "telescopes": {}
            },
        }
    }
    sample_config2 = {
        "site": "site2",
        "mounts": {
            "s2m1": {
                "telescopes": {}
            }, 
        }
    }
    sample_config3 = {
        "site": "site3",
        "mounts": {
            "s3m1": {
                "telescopes": {
                    "s3m1t1": {
                        "cameras": {
                            "cam1": {}
                        }
                    }
                }
            }, 
            "s3m2": {
                "telescopes": {
                    "s3m2t1": {
                        "cameras": {
                            "cam2": {}
                        }
                    }
                }
            }, 
            "s2m3": {
                "telescopes": {
                    "s3m3t1":{}
                }
            },
        }
    }
    sample_config5 = {
        "site": "site5",
        "mounts": {
            "mount1": {
                "telescopes": {
                    "t1": {
                        "cameras": {
                            "cam1": {
                                "type": "ccd",
                                "pixels": "2048",
                            },
                            "cam2": {
                                "type": "cmos",
                                "pixels": "8172",
                            },
                        },
                        "focusers": {
                            "foc1": {
                                "cameras": ["cam1", "cam2"]
                            }
                        }
                    },
                    "t2": {
                        "cameras": {}
                    }
                }
                
            },
            "mount2": {
                "telescopes": {
                    "t3": {
                        "cameras": {
                            "cam3": {
                                "type": "ccd",
                            }
                        }
                    }
                }
            },
        }
    }
    sample_config4 = {
        "site": "site4",
        "enclosures": ["enc1", "enc2"],
        "mounts": ["mount1", "mount2", "mount3"],
        "telescopes": ["t1", "t2", "t3", "t4"],
        "cameras": ["cam1", "cam2", "cam3", "cam4", "cam5"], 
        "filters": ["fil1", "fil2", "fil3", "fil4"],
        "flatscreens": ["flt1", "flt2", "flt3"],
        "focusers": ["foc1", "foc2", "foc3", "foc4"],
        "rotators": ["rot1", "rot2", "rot3"],
        "power_cycle_switch": ["pcs1", "pcs2", "pcs3"],
        "weather": ["wx1", "wx2"],
    }
    simple_config = {
        "site": "site4",
        "mount": {
            "mount1": {
                "name": "mount1",
                "driver": 'ASCOM.Simulator.Telescope',
            },
        },
        "camera": {
            "cam1": {
                "name": "cam1",
                "driver": 'ASCOM.Simulator.Camera',
            },
            "cam2": {
                "name": "cam2",
                "driver": 'ASCOM.Simulator.Camera',
            },
        },
        "filter": {
            "fil1": {
                "name": "fil1",
                "driver": "ASCOM.Simulator.Filter",
            }
        },
        "telescope": {
            "telescope1": {
                "name": "telescope1",
                "driver": "ASCOM.Simulator.Telescope"
            }
        }
    }
    sample_upload_request = {
        "object_name": "raw_data/2019/a_file2.txt"
    }

    # Each item is one request
    endpoints = [
        #{'uri': 'site1/config/', 'method': 'PUT', 'payload': sample_config},
        #{'uri': 'site2/config/', 'method': 'PUT', 'payload': sample_config2},
        #{'uri': 'site3/config/', 'method': 'PUT', 'payload': sample_config3},
        #{'uri': 'site4/config/', 'method': 'PUT', 'payload': sample_config4},
        #{'uri': 'site5/config/', 'method': 'PUT', 'payload': sample_config5},
        {'uri': 'site4/config/', 'method': 'PUT', 'payload': simple_config},

        #{'uri': 'site1/status/', 'method': 'PUT', 'payload': site_status},
        #{'uri': 'site1/weather/', 'method': 'PUT', 'payload': weather_status},

        {'uri': 'site1/mount1/command/', 'method': 'POST', 'payload': goto_cmd},

        #{'uri': 'site1/status/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/weather/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/mount1/command/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/config/', 'method': 'GET', 'payload': None},
        #{'uri': 'site1/upload/', 'method': 'GET', 'payload': sample_upload_request},
        {'uri': 'all/config/', 'method': 'GET', 'payload':None},
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
    if True: 
        body = {"object_name": "raw_data/2019/image001.fits"}
        print(c.post('site1/download/', body))
