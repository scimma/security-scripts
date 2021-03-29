#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

Options available via <command> --help
"""
import os
import boto3
import logging
from pathlib import Path
from threading import Lock
from security_scripts.information.lib import shlog

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

# enable process printing and counter
s_print_lock = Lock()
total_keys = 0
# define a global client to be defined later
client = None

from security_scripts.information import vault as vlt

def flow_vault_main(args):
    """Download flow logs into a local vault"""
    vlt.vault_main(args)


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    bucket = config.get("FLOW_DOWNLOAD", "bucket", fallback='s3://scimma-processes/flow-logs')
    vaultdir = config.get("DEFAULT", "flowvault", fallback="~/.flow_vault")
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")

    if remote:
        # augment remote parser with a new subcommand
        inf_vault_parser = parser.add_parser('inf_flow_vault', parents=[parent_parser], description=flow_vault_main.__doc__)
        inf_vault_parser.set_defaults(func=flow_vault_main)
        # arguments will be attached to subcommand
        target_parser = inf_vault_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--bucket', '-b', help='bucket with cloudtail logs (default: %(default)s)',default=bucket)
    target_parser.add_argument('--vaultdir', '-v',help='path to directory containing AWS logs (default: %(default)s)',default=vaultdir)
    target_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
    target_parser.add_argument('--servicefolder', '-sf',
                               help='Name of the folder the logging service uses (default: %(default)s)',
                               default='vpcflowlogs')
    return parser



if __name__ == "__main__":

   import argparse 
   import configparser

   """ get defaults from configuration system"""
   from security_scripts.kli import env_control
   config = configparser.ConfigParser()
   import os
   rel_path = "defaults.cfg"
   cfg_sources = [rel_path,  # built-in config for fallback
                  os.path.expanduser(env_control())  # env value
                  ]
   config.read(cfg_sources)

   profile  = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
   loglevel = config.get("DOWNLOAD", "loglevel",fallback="NORMAL")
   
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use (default: %(default)s)')
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                       default=loglevel,
                       choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])

   parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   shlog.basicConfig(level=args.loglevel)



   flow_vault_main(args)


