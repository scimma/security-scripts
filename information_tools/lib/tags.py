"""
Data Acquisition and Tests/Information for Scimma AWS Tagging

This module has code to collect data from all allowed
AWS regions and check that the tags needed for
AWS-level accounting and AWS-level incident response
are present.

"""

import boto3
import pandas as pd
import sqlite3
import aws_utils
import measurements
import shlog

class Tags(measurements.Dataset):
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "tags"
        
    def make_data(self):
        """
        Make a tabe called TAGS based on tagging data.
        Ths collection of data is based on teh resourcetaggingapi
        """ 
        shlog.normal("beginning to make %s data" % self.name) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "create table IF NOT EXISTS tags (short_arn text, tag text, value text, arn text)"
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages.
        self.args.session = boto3.Session(profile_name=self.args.profile)
        region_name_list = aws_utils.decribe_regions_df(self.args)['RegionName']
        for region_name in region_name_list:
            client = self.args.session.client('resourcegroupstaggingapi',region_name=region_name)
            paginator = client.get_paginator('get_resources')
            page_iterator = paginator.paginate()
            
            # Dig the data out, making one record fo each key, value pair.
            for page in page_iterator:
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




