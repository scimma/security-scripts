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
import json
import datetime
from security_scripts.information.lib import vanilla_utils

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
        enc = vanilla_utils.DateTimeEncoder  #converter fo datatime types -- not supported 
        for page in self._pages_all_regions('secretsmanager', 'list_secrets'):

            for secret in page['SecretList']:
                #import pdb; pdb.set_trace()                
                arn                = secret['ARN']
                short_arn          = aws_utils.shortened_arn(arn)
                region             = secret["ARN"].split(':')[3]
                name               = secret['Name']
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


        

