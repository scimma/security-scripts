"""

try to use Json labels from https://github.com/ocsf/ocsf-docs/blob/main/Understanding%20OCSF.pdf
only record IP's with at least one routable address.  
This code is "nearly ready" -- has to take DB table from environment.

"""

import json
import boto3
import zlib
from base64 import b64decode
import logging
import uuid
import os 
import ipaddress
import datetime
import time

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    #logger.setLevel(logging.DEBUG)
    event = decode(event["awslogs"]["data"])
    logger.debug("decoded event : {}".format(event))
    log_group = event['logGroup']
    flow_dict =    event['logEvents']
    for dict in flow_dict:
        logging.debug("dict:{}".format(dict))
        timestamp = dict['timestamp']  #aws timestamps are integar millisecs.
        if "NODATA" in dict['message']: continue
        flow = dict['message'].split(' ') 
        logging.debug("timestamp, flow: {}, {}".format(timestamp, flow))
        output = {}
        index = 0
        output['version']      =     flow[index];  index += 1
        output['account_id']   =     flow[index];  index += 1
        output['interface_id'] =     flow[index];  index += 1
        output['src_ip']       =     flow[index];  index += 1
        output['dst_ip']       =     flow[index];  index += 1
        output['src_port']     = int(flow[index]); index += 1
        output['dst_port']     = int(flow[index]); index += 1
        output['protocol']     = int(flow[index]); index += 1
        output['packet']       = int(flow[index]); index += 1
        output['bytes']        = int(flow[index]); index += 1
        output['start']        = int(flow[index]); index += 1
        output['end']          = int(flow[index]); index += 1
        output['action']       =     flow[index];  index += 1 
        output['log_status']   =     flow[index];  index += 1
        output['log_group']    = log_group
        output['_time']        = "{}".format(timestamp)  #..
                                 # ... time from epoch in msec.
        output['src_private']  = ipaddress.ip_address(output['src_ip']).is_private
        output['dst_private']  = ipaddress.ip_address(output['dst_ip']).is_private
        output['ref_time']     = "{}".format(timestamp) # string verison...
                                 #... required by standard original timestamp 
        output['uiud']         = "{}".format(uuid.uuid1())
        output['utc_date']      = datetime.datetime.fromtimestamp(time.time(), 
                                        tz=datetime.timezone.utc).isoformat()[:10]
        #additional from https://schema.ocsf.io/classes/network_activity?extensions=
        output["activity"]      = "network monitoring"
        output["activity_id"]   = 6  #traffic
        output['profile']       = ["flows"]
        output['type_uid']      = 400106
        output['type']          = "Network traffic report"
        output['src_endpoint']  = {"ip": output['src_ip'] , "port": output['src_port'] }
        output['dst_endpoint']  = {"ip": output['dst_ip'] , "port": output['dst_port'] }
        
        
        log_record =  json.dumps(output) 
        logging.debug("record: {}".format(log_record))
        #only log public IP's
        if  output['src_private'] and output['dst_private'] : 
            continue
        else:
            logging.info("routable IP:{}".format(log_record))
            status = load_log_item(output)
            logging.info("status: {}".format(status))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
        }
    
def decode(data):
    #inflate the cloudtrail event into useable JSON.
    compressed_payload = b64decode(data)
    json_payload = zlib.decompress(compressed_payload, 16+zlib.MAX_WBITS)
    return json.loads(json_payload)
    
    
def load_log_item(event, dynamodb=None):
    #load on record into dynamo db
    dynamodb = boto3.resource('dynamodb')
    os.environ["DB_TABLE"] = "OpsLogs_devel"
    table_name = os.getenv('DB_TABLE')
    table = dynamodb.Table(table_name)
    status = table.put_item(Item=event)
    return status

 
