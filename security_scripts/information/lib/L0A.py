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
import os

class Acquire(measurements.Dataset):
    """
    Load information from secrets manager api into a relational table.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "secrets"
        # dir enforcement
        self.f_path = args.report_path + '/L0A/'
        if not os.path.exists(self.f_path):
            os.makedirs(self.f_path)

        self.make_data()
        self.clean_data()

        
    def make_data(self):
        """
        """
        aws_paged_resources = commands.commands
        for resource, aspect, recipes in aws_paged_resources:
            records = []
            print ("TRYING {} , {}".format(resource, aspect))
            for page, _ in self.page_param_setter(resource, aspect, recipes):
                resource_name = resource
                record = self._json_clean_dumps(page)
                records.append(record)
                print ("HAVE_STUFF:{} {}".format(resource, aspect))
                # databse magic happens here
                for content in page:
                    if isinstance(page[content], list):
                        for item in page[content]:
                            self._insert_all_json(resource_name, aspect, self._json_clean_dumps(item))
                    #print ("SUCCESS {} , {}".format(resource, aspect))

            #Write the collection of records for thsi API call out
            records = ",".join(records)
            records = "[" + records + "]"
            filename = "{}_{}.json".format(resource, aspect)

            f = open(self.f_path + filename,"w")
            f.write(records)
            f.close()

        

