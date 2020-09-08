#!/usr/bin/env python
"""
Print S3 storage resource on stdout.

Beginning of a script to tell us more.

Options available via <command> --help
"""

import logging

       
def main(args):
   import subprocess
   
   logging.info(args)
   cmd = "aws s3api  list-buckets --profile {} --output json ".format(args.profile)
   logging.info(cmd)
   ret = subprocess.run(cmd, shell=True, check=True)
   

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
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   main(args)

