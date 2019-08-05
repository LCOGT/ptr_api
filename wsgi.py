# wsgi.py

# Required for ElasticBeanstalk deploy.

from application import application

if __name__ == "__main__":
    application.run()

