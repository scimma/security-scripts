#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

The command uses the shell "trailscraper", which provides
for incremental updates of the files. The command is
sensitive to a config file.

Options available via <command> --help
"""
import logging
import subprocess
import shlog

def main(args):
   """
   Download Cloudtrail logs to the vault directory.

   A vault file is bushy directory tree that is stored under
   $HOME/.trailscraper. teh leaves are (many jason) files, each
   covering a small slice of time. The files contain AWS event records.
   """
   # retrieve regions
   import regex as re
   import boto3
   args.session = boto3.Session(profile_name=args.profile)
   regions = au.decribe_regions_df(args)

   # translate security scripts arguments into trailscraper arguments
   # generate regions argument
   region_arg = ''
   for region in regions['RegionName']:
       region_arg += ' --region ' + region
    # translate verbosity level
   if args.loglevel == 'DEBUG':
       verbosity = '--verbose '
   else:
       verbosity = ''
   # regex the bucket and prefix
   try:
       ts_bucket = re.findall('(?<=s3:\/\/)(.*?)(?=\/)', args.bucket)[0]
       ts_prefix = re.findall('([^\/]+$)', args.bucket)[0]
   except IndexError:
       shlog.normal('error parsing bucket ' + args.bucket + ', s3://bucket/prefix format is expected')
       exit(0)

   cmd = "trailscraper " + verbosity + "download " \
         "--bucket " + ts_bucket + " " \
         "--prefix " + ts_prefix + "/ " \
         "--account-id " + args.accountid + " " \
         + region_arg
   logging.info(cmd)
   status = subprocess.run(cmd, shell=True)
   exit(status.returncode)

if __name__ == "__main__":

   import argparse 
   import configparser
   import aws_utils as au

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   vaultdir = config.get("DEFAULT", "vault directory", fallback="~/.trailscraper")
   profile  = config.get("DEFAULT", "profile", fallback="default")
   accountid = config.get("DOWNLOAD", "accountid",fallback="585193511743")
   loglevel = config.get("DOWNLOAD", "loglevel",fallback="INFO")
   bucket   = config.get("DOWNLOAD", "bucket")
   
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)
   parser.add_argument('--vaultdir'     ,help='vault directory def:%s' % vaultdir, default=vaultdir)
   parser.add_argument('--bucket'       ,help='bucket with cloudtail logs', default=bucket)
   parser.add_argument('--accountid', help='AWS account id', default=accountid)

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   main(args)

