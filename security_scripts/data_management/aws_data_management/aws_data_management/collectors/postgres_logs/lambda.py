"""
Clean postgres log events  from cloudwath and foreard to Dynamo DB

Cleaning  includesL         
    unpacking mulity log lines on log line per AWS record
    delteiing fielids containint no useful informations.
    settgin a time stamp useful for the dynamodb TTL feature

"""

import json
import time
import os 
from decimal import Decimal
import boto3
import zlib
from base64 import b64decode
import logging

# Information securty dats is retained for 3 months.
# the TTL retntions  is set in seconds in the future.
TTL_RETENTION_SEC = 3*30*24*60*60

def decode(data):
    #inflate the cloudtrail event into useable JSON.
    compressed_payload = b64decode(data)
    json_payload = zlib.decompress(compressed_payload, 16+zlib.MAX_WBITS)
    return json.loads(json_payload)

def load_log_item(event, dynamodb=None):
    #load on record into dynamo db
    dynamodb = boto3.resource('dynamodb')
    table_name = os.getenv('DB_TABLE')
    table = dynamodb.Table(table_name)
    table.put_item(Item=event)



def lambda_handler(event, context):
    # Unpack, flatten mulitp logfile entries into single-line records in dynamo db

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info("raw cloudwatch event : {}".format(event))
    event = decode(event["awslogs"]["data"])
    logger.info("decoded event : {}".format(event))

    
    # Fatten/cleand into one long entry per line                                                                                               
    # TBD if we can robustly parse the postgres log message                                                                            
    for entry in event["logEvents"]:
        j ={}  #clean dict (for sanity)
        j["messageType"]    = event["messageType"]
        j["logGroup"]       = event["logGroup"]
        j["logStream"]      = event["logGroup"]
        j["timestamp"]      = entry["timestamp"]
        j["message"]        = entry["message"]
        j["expTime"]        = entry["timestamp"] + TTL_RETENTION_SEC
        logger.info ("cleaned event {}".format(j))
        load_log_item(j)


