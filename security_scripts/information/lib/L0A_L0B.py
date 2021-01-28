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
import glob

class Acquire(measurements.Dataset):
    """
    Clean aquired data, elevating it from L0A to L0B

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "secrets"
        # dir enforcement
        self.s_path = args.report_path + '/L0A/'
        self.f_path = args.report_path + '/L0B/'
        if not os.path.exists(self.f_path):
            os.makedirs(self.f_path)

        self.make_data()
        self.clean_data()


    def to_L0B(self, records):
        cleaned = []
        for record in records:
            del record['ResponseMetadata']
            has_content = any([record[x] for x in record.keys()])
            if has_content: cleaned.append(record)
        return cleaned

    def json_to_file(self, fdir, fn, jlist):
        """
        Write a file given a list binary JSON objects.
        """
        jlist = [json.dumps(item) for item in jlist]
        jtext = ",".join(jlist)
        jtext = "[" + jtext + "]"
        L0B_file_name = os.path.join(fdir, fn)
        f = open(L0B_file_name, "w")
        f.write(jtext)
        f.close()

        
    def clean_data(self):
        """
        Main program
        -- Loop over all the L0A files
        -- Generate L0B files
        """
        for records, basefilename in self.jsons_from_dir(self.s_path):
            #process information to L0_B level for one L0A file.
            print("Cleaning {}".format(basefilename))
            records  = self.to_L0B(records)

            #Nothing there? then produce no L0B file
            if not records : continue

            # Extract meta data from (ugh) file name
            # string before the first _ is service
            # stings after the firt _ are methods
            metadata  = basefilename.replace(".json","")
            service   = metadata.split("_")[0]
            function = "_".join(metadata.split("_")[1:])
            context = {"service" : service, "function" : function}

            # place into L0B schema element of json
            # and acculate on list
            #import pdb; pdb.set_trace()
            #records["_context"]=context

            self.json_to_file(self.f_path, basefilename, records)

        

