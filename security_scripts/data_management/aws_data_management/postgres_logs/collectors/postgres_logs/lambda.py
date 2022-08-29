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
import uuid

# Information securty dats is retained for 3 months.
# the TTL retntions  is set in seconds in the future.
TTL_RETENTION_SEC = 3*30*24*60*60
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    status = table.put_item(Item=event)
    logger.info("put_timestatus : {}".format(status))



def lambda_handler(event, context):
    # Unpack, flatten multiple logfile entries into single-line records in dynamo db

    logger.info("raw cloudwatch event : {}".format(event))
    event = decode(event["awslogs"]["data"])
    logger.info("decoded event : {}".format(event))

    
    # Fatten/clean into one long entry per line                                                                                               
    # TBD if we can robustly parse the postgres log message                                                                            
    for entry in event["logEvents"]:
        if "checkpoint" in entry["message"] :
            logging.info ("dropping: {}".format(entry["message"]))
            continue
        j ={}  #clean dict (for sanity)
        j["messageType"]    = event["messageType"]
        j["logGroup"]       = event["logGroup"]
        j["logStream"]      = event["logGroup"]
        j["expTime"]        = int(time.time()) + TTL_RETENTION_SEC
        j["uuid"]           = str(uuid.uuid1())
        #
        # OSCF keywords below here
        # see https://schema.ocsf.io/categories/database?extensions=
        #
        j["activity"]       = "Logging event (filtered)"
        j["activity_id"]    = -1                  #other   
        j["_time"]          = entry["timestamp"]
        j["category"]       = "database"
        j["category_uid"]   = 7                   #Database Activity events.
        j["message"]        = entry["message"]
        j["profiles"]       = ["postgress_logs"]
        j["ref_time"]       = entry["message"][:19]
        logger.info ("cleaned event {}".format(j))
        load_log_item(j)


