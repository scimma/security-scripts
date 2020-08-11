#!/usr/bin/env python
"""
Update (or create) a vault directory populated withfiles
from cloudtrail logs.  

The command uses the shell "aws s3 sync", which provides
for incremental updates of the files,. The command is
snesitive to a config file. 

Options available via <command> --help
"""
import logging
import subprocess       

def main(args):
   """
   Download cloudtrail logs to the vault directory. 

   A vault file is a dictionary of "Records" containing an array
   of json objects.  A vault is a directory tree of some depth.
   """
   cmd = "aws s3 sync {}  {}  --profile {}"
   cmd = cmd.format(args.bucket, args.vaultdir, args.profile)
   logging.info(cmd)
   status = subprocess.run(cmd, shell=True)
   exit(status.returncode)

if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   vaultdir = config.get("DEFAULT", "vault directory", fallback="./vault")
   profile  = config.get("DEFAULT", "profile", fallback="sciimma-aws-admin")
   loglevel = config.get("DEFAULT", "loglevel",fallback="INFO")
   bucket   = config.get("DOWNLOAD", "bucket",fallback="s3://scimma-processes/Scimma-event-trail")
   
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help="Level for  reporning e.r DEBUG, INFO, WARN", default="INFO")
   parser.add_argument('--vaultdir'     ,help='vault directory def:%s' % vaultdir, default=vaultdir)
   parser.add_argument('--bucket'       ,help='bucket with cloudtail logs', default=bucket)

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   main(args)

