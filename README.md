# ptr_api

This repo contains Photon Ranch's RESTful API built using the Flask web framework. This API provides a method of communication between AWS and Photon Ranch's front-end web application as well as observatory-side applications.

## Getting Started

These instructions will get you a copy of the API up and running on your local machine for development and testing purposes.

### Setting up the project
To begin working, first acquire the ptr_api repository from github and set up a Python virtual environment.

##### Clone the repo
```bash
$ git clone 'repo url'
$ cd flask_api
```

##### Create Python virtual environment - version 3.6 or higher
```bash
$ mkdir venv
$ cd venv
$ python3.6 -m venv vitrual-environment-name
```

##### Activate the virtual environment
```bash
$ source venv/virtual-environment-name/bin/activate
```

### Install dependencies
Use the python package-management system in order to install the following required modules within the virtual environment:
```bash
$ pip install -r requirements.txt   
```


### Generate required config files
Next, it is neccesary to create certain config files that will hold environment variables to be used by the API as well as client application. The values for these variables can be obtained from the LCOGT System Information Sheet.

##### Create .auth_env
Instantiate and populate a file titled '.auth_env' within the main ptr-flask-api directory. This file provides identification information from Amazon Cognito in order for the API to have access to certain Amazon services, such as DynamoDB, SQS, and S3.
```
~ LOCAL_AWS = boolean indicating if you want to run a local aws instance (not recommended)
~ auth_REGION = region
~ auth_USERPOOL_ID = userpool id
~ auth_APP_CLIENT_ID = app client id
~ auth_APP_CLIENT_SECRET = app client secret
```

##### Create .client_env
Enter the directory labeled 'tests' in order to access the testing client application:
```bash
$ cd tests
```

Instantiate and populate a file titled '.client_env' within the tests directory. This file provides identification information from Amazon Cognito in order for the client application to test all endpoints specified by the API.
```
~ client_REGION = region
~ client_USERPOOL_ID = userpool id
~ client_APP_CLIENT_ID = app client id
~ client_APP_CLIENT_SECRET = app client secret
~ client_USERNAME = client username
~ client_PASS = client password
```

### Deploy and test the API
It should be possible to now host the API locally from any workspace by using the command:
```bash
$ flask run
```

In a seperate terminal, you can test the API by running the client.py script.
