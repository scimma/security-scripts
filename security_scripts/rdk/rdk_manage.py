#!/usr/bin/env python

"""
Manage the custom config deployments for SCIMMA.
This is a minimal implementation, to get us started.

The command executes one of rdk deploy modify or undeploy
for each of the current AWS regions had-configured into this file.
 
Options available via <command> --help

"""
import boto3, botocore
import shlog
import sys
import os



CODE_BUCKET_TEMPLATE="scimma-processes-{}"

def check_lambda_code_bucket_exists(args, bucket):
   # Check that there is an appropriatly named code bucket
   # for each region we will deploy to.
   # to-do check that it's in the region it's name implies.
    try:
        args.s3.meta.client.head_bucket(Bucket=bucket)
        shlog.normal("prerequisite bucket {} exists".format(bucket))
        return True
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            shlog.error("cannot access pre-requisite bucket {}".format(bucket))
            return False
        elif error_code == 404:
            shlog.error("pre-requisite bucket {} does not exist".format(bucket))
            return False

def main(args):
   "perform (or dry run) the indicated rdk command"

   #########################################################################
   # Check pre-condition -- check them all before quitting to have mercy and
   # allow parallel debug
   #########################################################################
   
   # Condition 1
   # Every region must have its own bucket to hold the lambda's code.
   # Don't thank me, thank aws.
   args.s3 = boto3.resource('s3')
   checks =  [check_lambda_code_bucket_exists(args, CODE_BUCKET_TEMPLATE.format(region)
                                              ) for region in args.regions]
   if not all(checks) : exit(1)

   #
   # Formulate the AWS command and run over the indicated regions.
   #
   for region in args.regions:
      bucket=CODE_BUCKET_TEMPLATE.format(region)
      cmd = "rdk --region {} {} {} --custom-code-bucket {}  ".format(region, args.rdkcmd, args.rdkrule, bucket)
      if not args.dry_run:
         shlog.normal(cmd)
         status = os.system(cmd)
         shlog.normal ("command status is".format(status))
      else:
         shlog.normal ("would have executed: \n {}".format(cmd))

          
if __name__ == "__main__":

   import argparse 
   import configparser
   

   """ get defaults from configuration system"""
   #from security_scripts.kli import env_control
   config = configparser.ConfigParser()
   import os
   #rel_path = "../information/defaults.cfg"
   #cfg_sources = [rel_path,  # built-in config for fallback
   #               os.path.expanduser(env_control())  # env value
   #               ]
   #config.read(cfg_sources)

   #profile  = config.get("TAG_REPORT", "profile")
   #loglevel = config.get("TAG_REPORT", "loglevel",fallback="NORMAL")
   loglevel="NORMAL"
   profile = "scimma-uiuc-aws-admin"
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                       default=loglevel,
                       choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--dry-run','-n',default=False, action='store_true',
                       help = "dry run just show what would me done")
   parser.add_argument('-r', '--regions', metavar='region',nargs='+',
                       default = ["us-east-1","us-west-2","us-east-2","us-west-1"],
                       help='perform command in these AWS regions')
   
   parser.add_argument('rdkcmd',  choices=['deploy', 'undeploy', 'modify'], metavar='rdkfunction',
                    help='RDK commands to apply everywhere')
   parser.add_argument('rdkrule', metavar='rdkrule',nargs='?',
                       help='RDK rule or ruleset (-a if not specified)')
   #parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   "use all rules if no rule or ruleset specified"
   if not args.rdkrule: args.rdkrule = "-a"
   shlog.basicConfig(level=shlog.LEVELDICT[args.loglevel])
   print (args)
   main(args)

