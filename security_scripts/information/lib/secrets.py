"""
Data Acquisition and Tests/Information for Scimma AWS Tagging

This module has code to collect data from all allowed
AWS regions and buid a relational database.

There is code to check that the tags needed for AWS-level
accounting and AWS-level incident response are present.

"""

import boto3
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
        sql = """CREATE TABLE secrets
              (
                 short_arn TEXT, region TEXT, name TEXT, description TEXT,
                 lastchangeddate TEXT, arn TEXT, record JSON
               )
              """
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages.
        for page, _ in self._pages_all_regions('secretsmanager', 'list_secrets'):

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
                record             = self._json_clean_dumps(record)
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
                # populate the all_json table 
                self._insert_all_json("secrets", short_arn, record) 

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
        return sql

    def json_secrets_report (self):
        "dump json structure"
        return "select record from secrets"

    def make_asset_secrets_format(self):
        """
        Make  table(s) for interetion into the master asset table.
        """
        shlog.normal("building table secret assets ")
        
        sql = '''
              CREATE TABLE asset_data_secrets AS
                SELECT
                    "R:Secret held in "||short_arn                               asset,
                                                                           description,
                    "D:Data providing access as described"              business_value,
                    "D:Unauthorized access to SCiMMA AWS accoun holder"       impact_c,
                    "C"                                                           type,
                    short_arn                                                  "where"
                 FROM secrets
               '''
        r = self.q.q(sql)


        

