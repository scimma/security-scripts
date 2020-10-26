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
from security_scripts.information.lib import aws_utils
from security_scripts.information.lib import measurements
from security_scripts.information.lib import shlog
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
        # dir enforcement
        self.s_path = args.report_path + '/L0B/s3_list_buckets.json'
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
        sql = "create table s3 (asset text, bucket text, arn text, region text, npolicies text, ngrants text, grants json, policy_status text, bucket_policy JSON, record JSON)"
        shlog.verbose(sql)
        self.q.q(sql)

        # get buckets from local storage
        response = self.json_from_file(self.s_path)[0]

        # still need to init
        session = boto3.Session(profile_name=self.args.profile)
        client = session.client('s3')


        # the rest is untouched - this module still makes boto3 requests. shoudl we keep this info locally?
        # should we pull it with L0A?
        #ignore the 'ResponseMetadata' == seems to be no pagination context in there.
        buckets = response["Buckets"]
        for bucket in buckets:
            name=bucket["Name"]
            # arn can be computed from aws partition (e.g aws, aws-us-gov) and bucket name
            arn="arn:{}:s3:::{}".format("aws",name)
            region = client.head_bucket(Bucket=name)['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
            grants = client.get_bucket_acl(Bucket=name)["Grants"]
            ngrants = len(grants)
            asset = "aws bucket:{}".format(name)
 
            try: 
                result = client.get_bucket_policy_status( Bucket=name)
                policy_status = result["PolicyStatus"]
                bucket_policy = client.get_bucket_policy(Bucket=name)["Policy"]
                npolicies = len(bucket_policy)
            except botocore.exceptions.ClientError:
                policy_status = {"IsPublic" : False}
                bucket_policy=  []
                npolicies = 0
            except:
                raise
            record = bucket
            record['BucketPolicy'] = policy_status
            record['PolicyStatus'] = bucket_policy
            record['Region']       = region
            record = self._json_clean_dumps(record)
    
            sql = '''INSERT INTO s3 VALUES (?,?,?,?,?,?,?,?,?,?)'''
            npolicies = "{}".format(npolicies)
            ngrants   = "{}".format(ngrants)
            
            list = (asset, name, arn, region,  npolicies,  ngrants,
                    json.dumps(grants), json.dumps(policy_status), json.dumps(bucket_policy), record)
            self.q.executemany(sql,[list])
            # populate the all_json table 
            self._insert_all_json("s3", name, record)
            
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
        return sql

        
    def xinf_s3_bucket_asset_format(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting on bucket in  asset formant")
        
        sql = '''
              SELECT
                     'R:Bucket Contents:'||bucket asset,
                     'D'                          type,
                     'R:'||region                 "where"
             FROM  s3
               '''
        self.df = self.q.q_to_df(sql)

    def xinf_s3_configuraton_asset_format(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting on bucket configuraiton in asset formant")
        
        sql = '''
              SELECT
                     'R:Bucket configuration:'||bucket                  asset,
                     'R:Num policies grants:'||npolicies||','||ngrants  description,
                     'R:Restrict Access to information'                 'Business Value', 
                     'D'                                                type,
                     'R:'||region                                       'where'
              FROM  s3
               '''

        self.df = self.q.q_to_df(sql)

    def json_s3_xreport(self):
        "make json file"
        return """
                SELECT record FROM s3
               """
