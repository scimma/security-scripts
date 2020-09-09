#!/usr/bin/env python
"""
Print S3 storage resource on stdout.

Beginning of a script to tell us more.

Options available via <command> --help
"""

import shlog
import boto3
import botocore
import sys

def main(args):

   # Retrieve the list of existing buckets
   s3 = boto3.client('s3')
   response = s3.list_buckets()

   # Output the bucket names
   print('Existing buckets:')
   for bucket in response['Buckets']:
      print(bucket)
      result = s3.get_bucket_acl(Bucket=bucket["Name"])["Owner"]
      print(result)
      try: 
         result = s3.get_bucket_policy(Bucket=bucket["Name"])
         print(result["Policy"])
      except botocore.exceptions.ClientError:
         print(sys.exc_info()[0])
      

if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("S3_REPORT",'profile', fallback='scimma-uiuc-aws-admin')
   loglevel = config.get("S3_REPORT", "loglevel",fallback="INFO")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--loglevel','-l',help=shlog.helptext, default="INFO")

   args = parser.parse_args()
   shlog.basicConfig(format="s3_report.py: %(message)s'", level=args.loglevel)

   main(args)

