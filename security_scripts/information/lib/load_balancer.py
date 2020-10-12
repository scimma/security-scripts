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
    Load information from load balancer api into a relational table.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "load_balancers"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        Make a table called load_balancer based on tagging data.
        This collection of data is based on the resourcetaggingapi

        If the tags table exists, then we take it data collection
        would result in duplicate rows. 
        """
        if self.does_table_exist():
            shlog.normal("load_balancers already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = """CREATE TABLE load_balancers
              (
                 name TEXT, vpc TEXT, record JSON
               )
              """
        shlog.verbose(sql)
        self.q.q(sql)

        # classic load balancers
        for page, _ in self._pages_all_regions('elb', 'describe_load_balancers'):
            for elb in page['LoadBalancerDescriptions']:
                # import pdb ; pdb.set_trace()
                name = elb['LoadBalancerName']
                vpc = elb['VPCId']
                record = elb
                record = self._json_clean_dumps(record)
                sql = """
                               INSERT INTO load_balancers VALUES (?, ?, ?)
                                 """
                list = (
                    name,
                    vpc,
                    record
                )
                shlog.verbose(sql)
                self.q.executemany(sql, [list])

        # application balancers
        for page, _ in self._pages_all_regions('elbv2', 'describe_load_balancers'):
            for elb in page['LoadBalancers']:
                #import pdb ; pdb.set_trace()
                name               = elb['LoadBalancerName']
                vpc                = elb['VpcId']
                type               = elb['Type']
                record             = elb
                record = self._json_clean_dumps(record)
                sql = """
                       INSERT INTO load_balancers VALUES (?, ?, ?)
                         """
                list = (
                        name,
                        vpc,
                        record
                        )
                shlog.verbose(sql)
                self.q.executemany(sql, [list])

class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

    def inf_load_balancer_summary(self):
        """
        Summary load Balancers
        """
        
        sql = '''
              SELECT name, vpc  FROM load_balancers
       '''
        return sql

    def json_load_balancer_report(self):
        """
        """
        sql = '''
        SELECT record  FROM load_balancers
        '''
        return sql


        

