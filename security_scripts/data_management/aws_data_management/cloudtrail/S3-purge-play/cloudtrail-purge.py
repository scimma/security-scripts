#!/usr/bin/env python
"""
Scrub the cloudwatch bucket of all files older than
the retention period.  It does this by looping over all
Keys, and deleting objects older than the retention
period.;

This can be time-consuming, but its simple and workks.
and makes few assumtions abotu the strucure of the
repository
"""

import boto3
import datetime
import pprint 
import logging
import time

TTL_DAYS = 90 #remove stuff older than these many days.


logger=logging.getLogger()
logging.basicConfig(level=logging.INFO)

def purge_all():
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')
    # note that a prefix is a limited inital string ...
    number_listed = 0
    number_deleted = 0
    start_time = time.time()

    # Loop over all the files under this directory
    # Tthese would include the the couldgtrail loogs and the digests.
    # n.b digests hold cryptological digests of the logs.
    response = paginator.paginate(Bucket="scimma-processes", Prefix="Scimma-event-trail/AWSLogs/585193511743/")
    for r in response:
        for item in r['Contents']:
            number_listed += 1
            last_modified = item['LastModified']
            key = item['Key']
            delta = datetime.datetime.now(datetime.timezone.utc) - last_modified
            if "CloudTrail" not in key: continue
            if delta.days < 90 : continue 
            logging.debug("age(days), object, object_time: {},{}.()".format(delta, key, last_modified))
            resp = client.delete_object(Bucket="scimma-processes", Key=key)
            number_deleted += 1
            if number_deleted % 1000 == 0:
                logging.info("number deleted, total time, deleded object: {} {} {}".format(
                    number_deleted, time.time()-start_time, key)
                             )
    #
    #  report some stats.
    #
    runtime = time.time()-start_time
    logging.info("Objects considered, deleted, runtime(sec): {} {} {}".format(
        number_listed,  number_deleted, runtime)
                 )


if __name__ == "__main__":
    purge_all()
