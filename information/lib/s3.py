"""
Data Acquisition and Tests/Information for Scimma AWS Tagging

This module has code to collect data from all allowed
AWS regions and buid a relational database.

There is code to check that the tags needed for AWS-level
accounting and AWS-level incident response are present.

"""

import boto3
import pandas as pd
import sqlite3
import aws_utils
import measurements
import shlog
import botocore
import json

class Acquire(measurements.Dataset):
    """
    Load information from the resource tagging api into a relational table.

    Optional method to clean the data of non-SCiMMA concerns.
    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "s3"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        Make a table called TAGS based on tagging data.
        This collection of data is based on the resourcetaggingapi

        If the tags table exists, then we take it data collection
        would result in duplicate rows. 
        """
        if self.does_table_exist():
            shlog.normal("tags data already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "create table s3 (bucket text, arn text, region text, grant json, policy_status text, bucket_policy json)"
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages
        session = boto3.Session(profile_name=self.args.profile)
        client = session.client('s3')
        response = client.list_buckets()

        #ignore the 'ResponseMetadata' == seems to be no pagination context in there.
        buckets = response["Buckets"]
        for bucket in buckets:
            name=bucket["Name"]
            # arn can be computed from aws partition (e.g aws, aws-us-gov) and bucket name
            arn="arn:{}:s3:::{}".format("aws",name)
            region = client.head_bucket(Bucket=name)['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
            grants = client.get_bucket_acl(Bucket=name)["Grants"]
            try: 
                result = client.get_bucket_policy_status( Bucket=name)
                policy_status = result["PolicyStatus"]
                bucket_policy = client.get_bucket_policy(Bucket=name)["Policy"]
            except botocore.exceptions.ClientError:
                policy_status = [{"Result" : "None"}]
                bucket_policy=  [{"Result" : "None"}]
            sql = '''INSERT INTO s3 VALUES (?,?,?,?,?,?)'''
            list = (name, arn, region, json.dumps(grants), json.dumps(policy_status), json.dumps(bucket_policy))
            self.q.executemany(sql,[list])
    
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)


    def inf_s3_summary(self):
        """
        Just list information about all the buckets
        """
        self.current_test = "general information on all S3 buckets"
        shlog.normal(self.current_test)
        
        sql = '''
              SELECT
                 * 
              FROM
                 s3
               '''
        self.df = self.q.q_to_df(sql)

        

