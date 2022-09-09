#!/usr/bin/env python
"""
Scrub the cloudwatch bucket of all files older than
the retention period.  It does this by using the
sprage model for cloud trail, teh code probed for keys
containing "region/year/month/date" consisnten with being
90 -100 datgs old.  It deltes evrything under those paths.

thsi saves time, and API-call fees  compared to looping
over all paths and finding objects over 90 days old.

"""

import boto3
import datetime
import pprint 
import logging
import time
import json

TTL_DAYS = 90 #remove stuff older than these many days.
BUCKET="scimma-processes"

logger=logging.getLogger()
logging.basicConfig(level=logging.INFO)

AZLIST=["ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
         "ap-south-1",     "ap-southeast-1", "ap-southeast-2",
         "ca-central-1",   "eu-central-1",   "eu-north-1",
         "eu-west-1",      "eu-west-2",      "eu-west-3",
         "sa-east-1",      "us-east-1"       "us-east-2",
         "us-west-1",      "us-west-2"
         ]

ROOTS = [
    "Scimma-event-trail/AWSLogs/585193511743/CloudTrail/{az}/{year}/{month}/{day}",
    "Scimma-event-trail/AWSLogs/585193511743/CloudTrail-Digest/{az}/{year}/{month}/{day}"
    ]


def lambda_handler(event, context):

    n_deletes = 0
    start_time = time.time()
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')    
    for root in next_root():
        page = paginator.paginate(Bucket=BUCKET, Prefix=root)
        for item in page:
            if 'Contents' not in item: continue
            logging.info("KeyCount:{KeyCount},Prefix:{Prefix}".format(**item))
            for object_record in item['Contents']:
                key = object_record['Key']
                resp = client.delete_object(Bucket=BUCKET, Key=key)
                if n_deletes & 100 == 0:
                    n_deletes += 1
                    logging.info ("deletes, key: {} {}".format(n_deletes, key))
            logging.info("total deletes so far:{}".format(n_deletes))
    runtime = time.time()-start_time
    logging.info("Objects deleted, runtime(sec): {} {}".format(
        n_deletes, runtime)
                 )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
                
                
def next_root():
    "iterate over all the zones and recent  dates  which may need a purge"
    for delay in  range(TTL_DAYS, TTL_DAYS+10):
        purgedate = datetime.date.today() - datetime.timedelta(days=delay)
        d =  {
            "year" :      purgedate.year           ,
            "month" : str(purgedate.month).zfill(2),
            "day" :   str(purgedate.day).zfill(2)  ,
        }
        logging.info("examining {year}/{month}/{day}".format(**d))
        for az in AZLIST :
            d["az"] = az
            for root in ROOTS :
              yield root.format(**d)



if __name__ == "__main__":
    lambda_handler(None, None)

