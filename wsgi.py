# wsgi.py

# Required for ElasticBeanstalk deploy.

from ptr_api.application import application

if __name__ == "__main__":
    application.run()

