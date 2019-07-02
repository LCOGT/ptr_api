# auth.py

from flask import request, jsonify, abort
from warrant import Cognito
from warrant.exceptions import TokenVerificationException
from functools import wraps
from dotenv import load_dotenv
import os
from os.path import join, dirname


# AWS cognito account info imported from .env
dotenv_path_authenv = join(dirname(__file__),'.auth_env')
load_dotenv(dotenv_path_authenv)
REGION = os.environ.get('auth_REGION')
USERPOOL_ID = os.environ.get('auth_USERPOOL_ID')
APP_CLIENT_ID = os.environ.get('auth_APP_CLIENT_ID')
APP_CLIENT_SECRET = os.environ.get('auth_APP_CLIENT_SECRET')

# Object (from warrant module) used to verify access tokens. 
cognito_helper = Cognito(USERPOOL_ID, APP_CLIENT_ID, 
                         client_secret=APP_CLIENT_SECRET, 
                         user_pool_region=REGION )

# This decorator only returns the decorated function if it has a valid 
# access token. Otherwise, it will return a 401 UNAUTHORIZED response..
def required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        headers = request.headers
        try:
            auth_header = headers['Authorization'] 
            access_token = auth_header.split()[-1]
            cognito_helper.verify_token(access_token, 'access_token', 'access')
            
            #groups = cognito_helper.client.admin_get_list_groups_for_user(Username=)
            return f(*args, **kwargs)
        # In case there's no authorization header.
        except KeyError as e:
            print('KeyError: No authorization header value present.')
            print(e)
            abort(401)
        # In case the token doesn't verify.
        except TokenVerificationException:
            print('TokenVerificationException: access token could not be verified.')
            abort(401)
    return wrapped
