#!/usr/bin/env python

"""
Manage the custom config deployments for SCIMMA.
This is a minimal implementation, to get us started.

The command executes one of rdk deploy modify or undeploy
for each of the current regions of interest.


Options available via <command> --help

"""
import boto3
#import shlog
import sys
import os

def main(args):
   "perform (or dry run) the indicated rdk command"
   for region in args.regions:
      cmd = "rdk --region {} {} {} ".format(region, args.rdkcmd, args.rdkrule)
      if not args.dry_run:
         print(cmd)
         status = os.system(cmd)
      else:
         print ("would have executed: \n {}".format(cmd))
          
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
                       default = ["us-west-1", "us-west-2", "us-east-1", "us-east-2"],
                       help='perform command in these AWS regions')
   
   parser.add_argument('rdkcmd',  choices=['deploy', 'undeploy', 'modify'], metavar='rdkfunction',
                    help='RDK commands to apply everywhere')
   parser.add_argument('rdkrule', metavar='rdkrule',nargs='?',
                       help='RDK rule or ruleset (-a if not specified)')
   #parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   "use all rules if no rule or ruleset specified"
   if not args.rdkrule: args.rdkrule = "-a"
   print (args)
   main(args)

