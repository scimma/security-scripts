"""
Data Acquisition and Tests/Information for Scimma AWS Tagging

This module has code to collect JSOn
and put it into the all_jason schema for all
resions 
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
from security_scripts.information.lib import commands

class Acquire(measurements.Dataset):
    """
    Load information from secrets manager api into a relational table.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "untagged_list"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        """
        if self.does_table_exist():
            shlog.normal("untagged_list already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name))
        # Prepare table for untagged onject list
        sql = """CREATE TABLE untagged_list
                      (
                         resource_name TEXT, id TEXT, json TEXT
                       )
                      """
        shlog.verbose(sql)
        self.q.q(sql)

        # analyze data from all_json
        sql = """SELECT resource_name, id, record as json
                    FROM all_json a
                    WHERE a.record like '%"Tags": []%' -- empty tags
                      OR a.record like '%"TagSet": []%' -- empty tagset
                      OR (a.record not like '%Tags":%' and a.record not like '%TagSet":%') -- no tag dicts
                      """
        df = self.q.q_to_df(sql)

        self.q.df_to_db(self.table_name, df)

        

