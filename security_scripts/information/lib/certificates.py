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
import botocore
import json
from security_scripts.information.lib import vanilla_utils

class Acquire(measurements.Dataset):
    """
    Load information from the certificates api into a relational table.

    Optional method to clean the data of non-SCiMMA concerns.
    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "certificates"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        Make a table called CERTIFICATES based on certificates held in AWS
        """
        if self.does_table_exist():
            shlog.normal("{} data already collected".format(self.table_name))
            return

        shlog.normal("beginning to make {} data".format(self.table_name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "CREATE TABLE certificates (domain text, arn text, short_arn text, inuseby text, record json)"
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages
        session = boto3.Session(profile_name=self.args.profile)
        client = session.client('acm')
        paginator = client.get_paginator('list_certificates')
        for response in paginator.paginate():
            for certificate in response['CertificateSummaryList']:
                arn = certificate["CertificateArn"]
                domain = certificate["DomainName"]
                short_arn = aws_utils.shortened_arn(arn)
                record = client.describe_certificate(CertificateArn=arn)
                record = record["Certificate"]
                inuseby = record["InUseBy"]
                inuseby = [aws_utils.shortened_arn(arn) for arn in inuseby]
                inuseby = ",".join(inuseby)
                enc = vanilla_utils.DateTimeEncoder
                record = json.dumps(record, cls=enc)
                #"CREATE TABLE certificates (domain text, arn text, short_arn text, inuseby text, record json)"
                sql = "INSERT INTO certificates VALUES (?, ?, ?, ?, ?)"
                params = (domain, arn, short_arn, inuseby, record)
                self.q.executemany(sql, [params])
                               
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

    def inf_certificate_summary(self):
        """
        Just list information about all the certificates
        """
        self.current_test = "general information on certificates"
        shlog.normal(self.current_test)
        
        sql = '''
              SELECT
                 * 
              FROM
                 certificates
               '''
        self.df = self.q.q_to_df(sql)

    def inf_certificate_asset_format(self):
        """
        Just list information in assed format
        """
        self.current_test = "certificate information in asset format"
        shlog.normal(self.current_test)
        
        sql = '''
              SELECT
                  'R: X509 cert for:'||domain    asset,
                  'R:Protects via:'||inuseby     description,
                  'C'                            type, 
                  'R:'||short_arn                "where"
              FROM
                 certificates
               '''
        self.df = self.q.q_to_df(sql)

        

