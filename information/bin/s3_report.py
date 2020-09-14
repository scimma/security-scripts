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
import json
import s3

def main(args):

   # Retrieve the list of existing buckets
   import vanilla_utils
   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile)
   import pdb; pdb.set_trace()
   x = s3.S3(args, "s3", q)
   exit()
   s3x = boto3.client('s3')
   response = s3.list_buckets()

   # Output the bucket names
   print('Existing buckets:')
   for bucket in response['Buckets']:
      name=bucket["Name"]
      # arn can be computed from aws partition (e.g aws, aws-us-gov) and bucket name
      arn="arn:{}:s3:::{}".format("aws",name)
      print("***", bucket, arn)
      #store "grants" as JSON
      result = s3.get_bucket_acl(Bucket=name)["Grants"]
      #not every line has display name
      #for r in result:
      #   print ("HEY", r, r["Grantee"]["DisplayName"])
      result = json.dumps(result, sort_keys=True, indent=4)
      print(result)
      region = client.head_bucket(Bucket=name)['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
      print(region)
      try: 
         result = s3.get_bucket_policy_status( Bucket=bucket["Name"])
         print("policy_status***", result["PolicyStatus"])
         result = s3.get_bucket_policy(Bucket=bucket["Name"])
         print("policy****",result["Policy"])
      except botocore.exceptions.ClientError:
         print("{'IsPublic': False}")  # the default if no policy.
      

if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("S3_REPORT",'profile', fallback='scimma-uiuc-aws-admin')
   loglevel = config.get("S3_REPORT", "loglevel",fallback="INFO")
   dbfile =   config.get("TAG_REPORT", "dbfile"  ,fallback=":memory:")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--loglevel','-l',help=shlog.helptext, default="INFO")
   parser.add_argument('--dbfile'       ,help='database file to use def:%s' % dbfile, default=dbfile)
   parser.add_argument('--dump'         ,help="dump data and quit, do not apply test", default=False, action='store_true' )
   parser.add_argument('--listonly'     ,help="list tests and quit", default=False, action='store_true' )
   parser.add_argument('--only'         ,help="only run reports matching glob", default="*")
   parser.add_argument('--bare'         ,help="print bare report, no wrap, no format", default=False, action='store_true')
   
   args = parser.parse_args()
   shlog.basicConfig(format="s3_report.py: %(message)s'", level=args.loglevel)

   main(args)

