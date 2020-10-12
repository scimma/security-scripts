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

class Acquire(measurements.Dataset):
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

        for page, _ in self._pages_all_regions('resourcegroupstaggingapi',  'get_resources'):

            ResourceMappingList = page['ResourceTagMappingList']
            for d in ResourceMappingList:
                full_arn = d['ResourceARN']
                short_arn = aws_utils.shortened_arn(d['ResourceARN'])
                for kvdict in d['Tags']:
                    sql = 'insert into tags values ("%s","%s","%s", "%s")' % (
                           short_arn, kvdict["Key"], kvdict["Value"], full_arn)
                    self.q.q(sql)

    def clean_data(self):
        """
        Remove items that are not relevant

        Tags with values beginning with uiuc-  are not set
        by the scimma project they are set by our UIUC AWS provider
        """

        shlog.normal("beginning to clean %s data" % self.name) 
        sql = '''
        DELETE FROM
            tags
        WHERE
             arn IN (
              SELECT DISTINCT arn FROM tags WHERE value LIKE "uiuc-%"
                    )
        '''
        self.q.q(sql)
        shlog.normal("%s data prepared" % self.name)
    
class Report(measurements.Measurement):
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
        return sql


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
        return sql


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
        return sql

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
        return sql

    def inf_tags_bound_to_secrets(self):
        """
        Show tags bound to secrets.

        Tagging can be used to control access to secrets.
        """

        shlog.normal("tags that are bund to secrets")
        sql = '''
            SELECT short_arn, tag, value, arn
            FROM
              tags
            WHERE arn like "%secret%"  
            ORDER BY arn
        '''
        return sql


    def make_asset_data_by_service(self):
        """
        Make  table(s) for insertion into the master asset table.
        """

        sql = """
          CREATE TABLE
            asset_data_by_service
          AS
            SELECT
                t1.value criticality,
                t2.value service,
                t3.value description,
                t1.short_arn asset
            FROM tags t1
            LEFT JOIN tags t2
                ON t1.arn = t2.arn
            LEFT JOIN tags t3
                ON t1.arn = t3.arn
            WHERE
                t1.tag   = 'Criticality'
            AND
                t2.tag = 'Service'
            AND
                t3.tag = 'Name'
            ORDER by t2.value
        """
        self.q.q(sql)

