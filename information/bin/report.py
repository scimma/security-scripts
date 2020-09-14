#!/usr/bin/env python
"""
Check consistenty of AWS implementation with SCIMMA rules.


Optons available via <command> --help
"""

import shlog

       
def main(args):
   import vanilla_utils
   import tags
   
   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile)

   tag_data = tags.Tags(args,"TAGS",q)
   if args.dump:
      tag_data.print_data()
      exit()


   a = tags.Test_standard_tags(args, "Tagging Rule Check", q)
   #import pdb; pdb.set_trace()
   

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
   shlog.basicConfig(level=args.loglevel)

   main(args)

