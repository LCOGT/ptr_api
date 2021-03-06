:warning: **This code is deprecated.** It has been replaced by [photonranch-api](https://github.com/LCOGT/photonranch-api). 

# ptr_api

This repo contains Photon Ranch's API built using the Flask web framework. This API provides a method of communication between AWS and Photon Ranch's front-end web application as well as observatory-side applications.

## Getting Started

These instructions will get you a copy of the API up and running on your local machine for use and development as well as a client application for testing purposes.

### Setting up the API
To begin working, first acquire the ptr_api repository from github and set up a Python virtual environment.

##### Clone the repo
```bash
$ git clone https://github.com/LCOGT/ptr_api.git
$ cd ptr_api
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
Use the python package-management system in order to install required modules within the virtual environment:
```bash
(venv)$ pip install -r requirements.txt   
```

### Generate required config files
In order to run and test the API, two seperate config files must be created. One config file will be read in by the API's main application and one will be used by the client application for testing. These files will hold authentication credentials to be loaded in as environment variables. The values for these variables can be obtained from the LCOGT System Information Sheet.

In order to setup the config file for the main application, first locate the file titled '.envDEFAULT' and make new copy of it. Rename the copy simply '.env'. You should notice that this file is no longer being tracked by git. Do not modify or remove the original .envDEFAULT file unless you are changing the way config variables are to be read in by the API. Populate the file .env appropriately using information located in the System Information Sheet under the ptr tab.

The second config file deals with testing and is outlined later on.


### Deploying the API
It should be possible to now host the API locally from any workspace by using the command:
```bash
(venv)$ flask run
```
<br/>


## Testing the API

### Create .client_env
Enter the directory labeled 'tests' in order to access the testing client application:
```bash
(venv)$ cd tests
```

Instantiate and populate a second config file titled '.client_env' within the tests directory. This file provides identification information from Amazon Cognito in order for the client application to access the API and test all endpoints.
```
~ client_REGION = region
~ client_USERPOOL_ID = userpool id
~ client_APP_CLIENT_ID = app client id
~ client_APP_CLIENT_SECRET = app client secret
~ client_USERNAME = client username
~ client_PASS = client password
```

### Unit tests
To run the unit tests, begin by going into the tests directory and start the mock AWS servers
```bash
(venv)$ python start_local.py
```

in a separate terminal, then run
```bash
(venv)$ pytest
```  

### Testing the endpoints
You can test the endpoints using the test client. This will test the local version of the API.
Make sure that you have the app running before you use the test client
```bash
(venv)$ flask run
```
Then go into the tests directory and run the test client
```bash
(venv)$ python client.py
```
An interface should appear allowing you to select the endpoints that you want to test (the "Test all endpoints" checkbox is currently not working).

## Endpoints

### Image Package Structure
When calling an endpoint that returns image information, an image package will be returned in the following structure:
```
{
  "recency_order": sort order index used by UI, integer
  "image_id": pk in images table, integer
  "site": site name, 3 characters
  "base_filename": root image name, 26 characters ex: "wmd-gf01-20190909-00005259"
  "capture_date": date of capture, string (javascript-ready timestamp)
  "sort_date": date of capture, string (javascript-ready timestamp)
  "right_ascension": right_ascension, double precision
  "declination": declination, double precision
  "altitude": altitude, double precision
  "azimuth": azimuth, double presicion
  "header": JSON of full header
  "filter_used": filter_used, string
  "airmass": airmass, double precision
  "exposure_time": exposure_time, double precision
  "created_user": created_user, integer (pk for user information in database)
  "jpg13_url": jpg13_url, string
  "fits13_url": fits13_url, string
}
```
All attributes present in the images table within the ptr database are placed inside the image package except for the booleans ex01_fits_exists, ex13_fits_exists, and ex13_jpg_exists. Instead, the two extra fields jpg13_url and fits13_url are appended to the end of the package for use when downloading images from S3. Some date formatting is also done before the image package is sent: capture_date and sort_date are converted to a javascript-ready timestamp (eg. miliseconds).
