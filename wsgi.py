# wsgi.py

# Required for ElasticBeanstalk deploy.

from app import application

if __name__ == "__main__":
    application.run()

