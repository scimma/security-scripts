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
        for resource, aspect, _  in aws_paged_resources:
            records = []
            print ("TRYING {} , {}".format(resource, aspect))
            for page, _ in self._pages_all_regions(resource, aspect):
                resource_name = resource
                record = self._json_clean_dumps(page)
                records.append(record)
                print ("HAVE_STUFF:{} {}".format(resource, aspect))
                self._insert_all_json(resource_name, aspect, record)
                    #print ("SUCCESS {} , {}".format(resource, aspect))
            #Write the collection of records for thsi API call out
            records = ",".join(records)
            records = "[" + records + "]"
            filename = "{}_{}.json".format(resource, aspect)
            f = open(filename,"w")
            f.write(records)
            f.close()

        

