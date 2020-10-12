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
        self.table_name = "secrets"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        """
        aws_paged_resources = commands.commands
        for resource, aspect, keys  in aws_paged_resources:
            print ("TRYING {} , {}".format(resource, aspect))
            for page, _ in self._pages_all_regions(resource, aspect):
                for k in page.keys():
                    if k is 'ResponseMetadata': continue
                    resource_name = resource
                    kind = "{}_{}".format(aspect, k)
                    record = self._json_clean_dumps(page[k])
                    print ("HAVE_STUFF:{} {} {}".format(resource, aspect, k))
                    self._insert_all_json(resource_name, kind, record)
                    #print ("SUCCESS {} , {}".format(resource, aspect))


        

