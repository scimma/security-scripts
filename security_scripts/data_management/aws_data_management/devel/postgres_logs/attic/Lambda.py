import json
import time

from decimal import Decimal
import json
import boto3

import zlib
import json
from base64 import b64decode

def decode(data):
    compressed_payload = b64decode(data)
    json_payload = zlib.decompress(compressed_payload, 16+zlib.MAX_WBITS)
    return json.loads(json_payload)

def load_log_item(event, dynamodb=None):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('DLP-test-log-accumulation')
    table.put_item(Item=event)



def lambda_handler(event, context):
    # TODO implement
    print("#######  HELP ##########")
    print("######## event : {}".format(event))
    print()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    event = decode(event["awslogs"]["M"]["data"]["S"])
    e = {"Time":current_time, "Source":"test", "Event":event}
    print("######## e: {}".format(e))
    load_log_item(e)
    print(current_time)
  
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! {}'.format(current_time))
   

    }

