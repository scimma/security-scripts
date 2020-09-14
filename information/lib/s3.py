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

class S3(measurements.Dataset):
    """
    Load information from the resource tagging api into a relational table.

    Optional method to clean the data of non-SCiMMA concerns.
    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "tags"
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
        sql = "create table tags (short_arn text, tag text, value text, arn text)"
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages
        session = boto3.Session(profile_name=self.args.profile)
        client = session.client('s3')
        response = client.list_buckets()
        import pdb; pdb.set_trace()

        #ignore the 'ResponseMetadata' == seems to be no pagination context in there.
        buckets = response["Buckets"]
        for bucket in buckets:
            name=bucket["Name"]
            # arn can be computed from aws partition (e.g aws, aws-us-gov) and bucket name
            arn="arn:{}:s3:::{}".format("aws",name)
            print("***", bucket, arn)
            region = client.head_bucket(Bucket=name)['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
            print(region)
            try: 
                result = client.get_bucket_policy_status( Bucket=name)
                print("policy_status***", result["PolicyStatus"])
                result = client.get_bucket_policy(Bucket=name)
                print("policy****",result["Policy"])
            except botocore.exceptions.ClientError:
                print("{'IsPublic': False}")  # the default if no policy.


    
class Test_standard_tags(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

    def tst_has_standard_tags(self):
        """
        Test for ARN's missing either Critiality or Service tags.
        """
        shlog.normal("performing test for Criticality and Service Tags")

        sql = '''
              SELECT
                 short_arn, tag, value, arn
              FROM
                 tags
              WHERE arn NOT IN
                 (select ARN from tags where tag = "Criticality"
                    INTERSECT
                  select ARN from tags where tag = "Service"
                 )
               '''
        self.df = self.q.q_to_df(sql)


    def tst_has_standard_criticality(self):
        """
        Test for ARN's that have criticality, but not one of the standard values
        """
        shlog.normal("looking for non standard criticality values")

        sql = '''
              SELECT
                 short_arn, tag, value
              FROM
                 tags
              WHERE  tag = "Criticality"
                 AND
                     value not in ("Development", "Demonstration", "Production", "Investigation")

               '''
        self.df = self.q.q_to_df(sql)


    def inf_service_names(self):
        """
        List unique service names found tags in the running system
        """
        shlog.normal("Reporting on unique service names")
        
        sql = '''
              SELECT
                 distinct value 
              FROM
                 tags
              WHERE  tag = "Service"

               '''
        self.df = self.q.q_to_df(sql)

    def inf_service_resources(self):
        """
        List AWS resources associated with services.
        """
        shlog.normal("Reporting resources associated with a service")
        
        sql = '''
              SELECT value, short_arn, arn
              FROM
                 tags
              WHERE  tag = "Service"
              ORDER by value, arn

               '''
        self.df = self.q.q_to_df(sql)


        

