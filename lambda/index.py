import json
import boto3
import os
import pprint

def handler(event, context):
    pprint.pprint("event")
    pprint.pprint(event)
    pprint.pprint("context")
    pprint.pprint(context)
    
    return 0