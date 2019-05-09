import boto3
import threading, subprocess
from moto import mock_sqs, mock_s3, mock_dynamodb2


def start_s3(port=5001):
    subprocess.call(["moto_server", "s3", f"-p{port}"])
def start_sqs(port=5002):
    subprocess.call(["moto_server", "sqs", f"-p{port}"])
def start_dynamodb(port=5003):
    subprocess.call(["moto_server", "dynamodb2", f"-p{port}"])

s3 = threading.Thread(target=start_s3)
sqs = threading.Thread(target=start_sqs)
dynamodb = threading.Thread(target=start_dynamodb)

s3.start()
sqs.start()
dynamodb.start()