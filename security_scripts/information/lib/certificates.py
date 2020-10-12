"""
Data Acquisition and Tests/Information for Scimma AWS Tagging

This module has code to collect data from all allowed
AWS regions and buid a relational database.

There is code to check that the tags needed for AWS-level
Accounting and AWS-level incident response are present.

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
        #import pdb; pdb.set_trace()
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = """CREATE TABLE certificates (asset text, domain text,
                            arn text, short_arn text, inuseby text, hash text, record json)"""
        shlog.verbose(sql)
        self.q.q(sql)

        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages
        for page, client in self._pages_all_regions('acm', 'list_certificates'):
            for certificate in page['CertificateSummaryList']:
                arn = certificate["CertificateArn"]
                domain = certificate["DomainName"]
                short_arn = aws_utils.shortened_arn(arn)
                record = client.describe_certificate(CertificateArn=arn)
                record = record["Certificate"]
                inuseby = record["InUseBy"]
                inuseby = [aws_utils.shortened_arn(arn) for arn in inuseby]
                inuseby = ",".join(inuseby)
                asset = "Cert:{} for use by {}".format(domain, inuseby)
                hash = vanilla_utils.tiny_hash(arn)
                record = self._json_clean_dumps(record)
                sql = "INSERT INTO certificates VALUES (?, ?, ?, ?, ?, ?, ?)"
                params = (asset, domain, arn, short_arn, inuseby, hash, record)
                self.q.executemany(sql, [params])
                # populate the all_json table 
                self._insert_all_json("certificate", short_arn, record) 

        
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
        return sql
    
    def make_asset_format(self):
        """
        Create asset format from fundamental descriptive data
        """
        sql = '''
              CREATE TABLE asset_data_certificates AS
              SELECT
                  'R:AWS users w/ authority to read/modify X509 cert for:'||domain    asset,
                  'R:Protects via:'||inuseby               description,
                  'D:Assures endpoint is Scimma endpoint'  business_value,
                  'D:Attacker might spoof Scimma Service'  impact_c,
                  'C'                                      type, 
                  'R:'||short_arn                          "where"
              FROM
                 certificates
               '''
        shlog.vverbose(sql)
        self.q.q(sql)

    def json_certificate_data(self):
        "make json file"
        return "select record from certificates"
