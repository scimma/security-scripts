#!/usr/bin/env python
"""
provides  variety  of checks and reports about
AWS usage for Information Security and AWS
Resource Management 


Optons available via <command> --help
"""

import shlog

       
def main(args):
   import vanilla_utils
   import tags
   import s3
   
   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile)

   tag_acquire = tags.Tags(args,"TAGS",q)
   s3_acquire = s3.S3(args, "s3", q)
   if args.dump:
      tag_acquire.print_data()
      s3_acquire.print_data()
      exit()

   # reporting actions are driven by instanitating the classes.
   tag_reports = tags.Test_standard_tags(args, "Tagging Rule Check", q)
   s3_reports=s3.Report_s3(args, "s3", q)   
   

if __name__ == "__main__":

   import argparse 
   import configparser

   """ get defaults from configuration system"""
   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("TAG_REPORT", "profile")
   loglevel = config.get("TAG_REPORT", "loglevel",fallback="NORMAL")
   dbfile =   config.get("TAG_REPORT", "dbfile"  ,fallback=":memory:")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help=shlog.helptext, default="NORMAL")
   parser.add_argument('--dbfile'       ,help='database file to use def:%s' % dbfile, default=dbfile)
   parser.add_argument('--dump'         ,help="dump data and quit, do not apply test", default=False, action='store_true' )
   parser.add_argument('--listonly'     ,help="list tests and quit", default=False, action='store_true' )
   parser.add_argument('--only'         ,help="only run reports matching glob", default="*")
   parser.add_argument('--bare'         ,help="print bare report, no wrap, no format", default=False, action='store_true')

   args = parser.parse_args()
   print (args)
   shlog.basicConfig(level=args.loglevel)

   main(args)

