#!/usr/bin/env python
"""
Print S3 storage resource on stdout.

Beginning of a script to tell us more.

Options available via <command> --help
"""

import logging

       
def s3_main(args):
   """Print S3 storage resource on stdout."""
   import subprocess
   
   logging.info(args)
   cmd = "aws s3api  list-buckets --profile {} --output json ".format(args.profile)
   logging.info(cmd)
   ret = subprocess.run(cmd, shell=True, check=True)


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    if remote:
        # augment remote parser with a new subcommand
        inf_s3_parser = parser.add_parser('inf_s3', parents=[parent_parser], description=s3_main.__doc__)
        inf_s3_parser.set_defaults(func=s3_main)
    return parser


if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("DEFAULT",'profile', fallback='scimma-uiuc-aws-admin')
   loglevel = config.get("S3_REPORT", "loglevel",fallback="INFO")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile, help='aws profile to use (default: %(default)s)')
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN (default: %(default)s)", default=loglevel)

   # no need to augment parser further
   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   s3_main(args)

