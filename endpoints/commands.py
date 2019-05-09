from aws import sqs
from flask import request
import json

# NOTE: queue names follow the convention {sitename}_{mountname}_queue.fifo
# For example: site1_mount1_queue.fifo

def get_command(site, mount='mount1'):
    queue_name = f"{site}_{mount}_queue.fifo"
    content = sqs.get_queue_item(queue_name)
    if content is not False:
        return (content) 
    return json.dumps({"Body": "empty"})

def post_command(site, mount='mount1'):
    queue_name = f"{site}_{mount}_queue.fifo"
    content = json.loads(request.get_data())
    res = sqs.send_to_queue(queue_name, json.dumps(content))
    return json.dumps(res)

