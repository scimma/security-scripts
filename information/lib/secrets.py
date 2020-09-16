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
import json
import datetime
import vanilla_utils

class Acquire(measurements.Dataset):
    """
    Load information from secrets manager api into a relational table.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "secrets"
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
            shlog.normal("secretsdata already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "CREATE TABLE secrets (short_arn text, region text, name text, description text, lastchangeddate text, arn text, record json)"
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages.
        self.args.session = boto3.Session(profile_name=self.args.profile)
        region_name_list = aws_utils.decribe_regions_df(self.args)['RegionName']
        for region_name in region_name_list:
            client = self.args.session.client('secretsmanager',region_name=region_name)
            paginator = client.get_paginator('list_secrets')
            page_iterator = paginator.paginate()
            
            # Dig the data out, making one record fo each key, value pair.
            # enc handles the datetiem classes in AWS json, turns them to ISO strings
            enc = vanilla_utils.DateTimeEncoder 
            for page in page_iterator:
                for secret in page['SecretList']:
                    arn                = secret['ARN']
                    short_arn          = aws_utils.shortened_arn(arn)
                    region             = region_name
                    name               = secret['Name']
                    #import pdb; pdb.set_trace()
                    description        = secret['Description']
                    lastchangeddate    = datetime.datetime.isoformat(secret['LastChangedDate'])
                    record             = secret
                    record["FlatTags"] = vanilla_utils.flatten_tags(secret["Tags"])
                    record             = json.dumps(secret, cls=enc)
                    sql = """
                       INSERT INTO secrets VALUES (?, ?, ?, ?, ?, ?, ?)
                         """
                    list = (short_arn,
                            region,
                            name,
                            description,
                            lastchangeddate,
                            arn,
                            record)
                    shlog.verbose(sql)
                    self.q.executemany(sql, [list])

class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

 

    def inf_secrets_summary(self):
        """
        Summary Report on Secrets
        """
        shlog.normal("Reporting secrets")
        
        sql = '''
              SELECT * FROM secrets
               '''
        self.df = self.q.q_to_df(sql)

    def inf_secrets_asset_format(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting in asset foramant")
        
        sql = '''
              SELECT name asset, description, "C" type, short_arn "where" from secrets
               '''
        self.df = self.q.q_to_df(sql)


        

