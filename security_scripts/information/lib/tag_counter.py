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
        self.table_name = "tag_counter"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        """
        if self.does_table_exist():
            shlog.normal("tag_counter already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name))
        # Prepare table for tag count analysis output
        sql = """CREATE TABLE tag_counter
                      (
                         service TEXT, request TEXT, total TEXT, untagged TEXT, tagged TEXT
                       )
                      """
        shlog.verbose(sql)
        self.q.q(sql)

        # analyze data from all_json
        sql = """WITH untagged(resource,id, cnt) AS (
                    SELECT resource_name, id, count(record) as cnt
                    FROM all_json a
                    WHERE a.record like '%"Tags": []%' -- empty tags
                      OR a.record like '%"TagSet": []%' -- empty tagset
                      OR (a.record not like '%Tags":%' and a.record not like '%TagSet":%') -- no tag dicts
                    GROUP BY resource_name, id
                ),
                     tagged(resource, id, cnt) AS (
                    SELECT resource_name, id, count(record) as cnt
                    FROM all_json a
                    WHERE a.record like '%"Tags": [{%' -- empty tags
                      OR a.record like '%"TagSet": [{%' -- empty tagset
                    GROUP BY resource_name, id
                     ),
                
                     all_count(resource, id, cnt) AS (
                    SELECT resource_name, id, count(record) as cnt
                    FROM all_json a
                    GROUP BY resource_name, id
                     )
                
                SELECT a.resource, a.id, a.cnt as total,
                       ifnull(u.cnt, 0) as untagged,
                       ifnull(t.cnt,0) as tagged
                    FROM all_count a
                    LEFT JOIN untagged u on u.resource = a.resource and u.id = a.id
                    LEFT JOIN tagged t on t.resource = a.resource and t.id = a.id
                    GROUP BY a.resource, a.id
        """
        df = self.q.q_to_df(sql)

        self.q.df_to_db(self.table_name, df)



class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

    def inf_tag_counter(self):
        """
        Test for ARN's missing either Critiality or Service tags.
        """
        shlog.normal("printing tagged/untagged resource count form the db")

        sql = '''
              SELECT *
              FROM tag_counter
               '''
        return sql
        

