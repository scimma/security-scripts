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
   q=vanilla_utils.Q(args.dbfile)

   tag_data = tags.Tags(args,"TAGS",q)
   tag_data.make_data()
   tag_data.clean_data()
   if args.dump:
      tag_data.print_data()
      exit()


   a = tags.Test_standard_tags(args, "Tagging Rule Check", q)
   #import pdb; pdb.set_trace()
   

if __name__ == "__main__":

   import argparse 
   import configparser

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
   parser.add_argument('--only'         ,help="only run reports matching glob", default="*")

   args = parser.parse_args()
   shlog.basicConfig(level=args.loglevel)

   main(args)

