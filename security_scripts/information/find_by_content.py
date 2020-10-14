#!/usr/bin/env python
"""
Search the cloudtrail vault for strings
with the value given by searchglob.

Perform caseblind search if indicated.
Truncate matched string if indicated.

ptions available via <command> --help
"""

import logging
import json
from datetime import date,timedelta
import os
from security_scripts.information.lib import shlog

class Cmp:
   """
    make a optiony case blind comparison of two strings using a glob

    """

   def __init__(self, args):
        self.caseblind     = args.caseblind
        self.searchglob    = args.searchglob
        if self.caseblind: self.searchglob.upper()
        
   def match(self, value):
       import fnmatch
       # Determine if string is a match
       # Set self.matched to most recent matched string.
       if type(value) is not type("") :
            #bullet proof unexpected type
           value = "%s" % value
       cmp_value = value
       if self.caseblind: cmp_value = value.upper()
       isMatch=  fnmatch.fnmatch(cmp_value, self.searchglob)
       if isMatch:
           self.matched = value
       else:
           self.matched = ""
       return isMatch

def find_string(obj, valuematch, c):
    """
    Return a list of key, value pairs where value matches valuematch
   
   Valuematch can be specifies as a glob style "wildcard"
    """
    import copy
    arr = []
    context = []


    def match(obj, arr, valuematch, c):
        """Recursively search for values"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    #recurr if composite type
                    match(v, arr, valuematch, c )
                elif c.match(v):
                    # save base type that matches
                    arr.append([k, c.matched])
                else:
                    # no match, let go
                    pass
                    shlog.vverbose("skipping: %s", v)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    #recurr if composite type
                    match(item, arr, valuematch, c)
                elif c.match(item):
                    # is it a basetype that matches?
                    arr.append([c.matched])
                else:
                    # no match, let it go
                    pass
                    shlog.vverbose("skipping: %s", item)
        return arr

    results = match(obj, arr, valuematch, c)
    return results

################################################################
#
#
###############################################################
def time_ordered_event_archives(args, template_path):
   """
   Return  a list of paths, sorted by increasing date.
   
   Construct the list based the template (ie  havig  wildcards),
   Considering only the first timestamp in the file holding the events.
   Given the vault files are small timeslices, this should  produce an
   event strean that is "pretty good" nearly time ordered.
   """
   import os
   import glob
   import gzip
   

   template_path = os.path.expanduser(template_path)
   list = []
   for path in glob.glob(template_path):
      with gzip.open(path, 'rb') as f:
         data = json.loads(f.read())
         list.append ("{} {}".format(data["Records"][0]["eventTime"], path))
   list.sort() #sort on date
   list = [l.split(" ") for l in list]
   if list != []:
        shlog.vverbose("first date, file available is {}".format(list[0] ))
        shlog.vverbose("last  date, file available is {}".format(list[-1]))
   return [ l[1] for l in list ]

###################################################################
#
#
###################################################################

def  get_all_template_paths(args):
   """
   Return a globbed path to all event files for each  date.

   The template covers all AWS regions.
   e.g  logs/Scimma-event-trail/AWSLogs/acct_id/CloudTrail/*/2020/08/20/*.json.gz
   """
   from pathlib import Path
   import glob
   args.datepath = "logs/Scimma-event-trail/AWSLogs/" + args.accountid + "/CloudTrail/"
   root = os.path.join(args.vaultdir, args.datepath)
   root = Path(os.path.expanduser(root)) # gt rit of any laeding ~
   root = "{}".format(root)              # go figure have to make it a string
   dir_filter = os.path.join(root,'*/20[0-9][0-9]/[0-9][0-9]/[0-9][0-9]/')
   paths = {os.path.dirname(p)  for p in glob.glob(dir_filter)}  # all paths into  set
   paths = {p.replace(root,'') for p in paths}                   # reduce to unique site/y/m/d
   paths = {os.path.join(*p.split('/')[2:]) for p in  paths}     # strip off site
   #Now path is just the date component e.g 2020/08/22, one for each date in the store
   #Compose into full template
   paths  = [os.path.join(args.vaultdir,args.datepath,"*",p,"*.json.gz") for p in  paths]
   paths.sort()                                                  # assure oldset to recent 
   return paths


def filter_template_paths_by_date_range(args, all_paths):
   """
   Filter a list  of template paths, retaining those consitent with user-supplied date range

   
   """
   anchor_date = args.date
   datedelta = args.datedelta
   if datedelta == 0 : return all_paths
   if datedelta < 0:
      range_parameters = [datedelta, 1]
   else:
      range_parameters =  [0, datedelta + 1]
   dates = [anchor_date + timedelta(days=i) for i in range(*range_parameters) ]
   dates = ["{}".format(d) for d in dates]
   dates = [d.replace("-", "/") for d in dates]
   shlog.normal("requested dates {}".format(dates))
   filtered = []
   for p in all_paths          :
      for d in dates:
         if d in p:
            filtered.append(p)
            shlog.debug('path used satified {}'.format(p))
            break

   return filtered



def find_main(args):
   """Dump cloudtail json event records from the vault having
   some value matching the globstring.

   A vault file is a dictionary of "Records" containing an array
   of json objects, one json object per cloudtrail event.
   There is a large variety of events, each with a
   different json schema."""
   import gzip

   c = Cmp(args)
   if not any(ext in args.searchglob for ext in ["*", "?"]):
       shlog.normal(args.searchglob + " does not have an * or ?")

   all_template_paths = get_all_template_paths(args)
   filtered_template_paths = filter_template_paths_by_date_range(args, all_template_paths)
   nitems = 0
   nfound = 0 
   for template_path in filtered_template_paths:
      for file in time_ordered_event_archives(args, template_path):
       with gzip.open(file, 'rb') as f:
           data = json.loads(f.read())
           for item in data['Records']:
              nitems += 1
              result = find_string(item, args.searchglob, c)
              if result :
                 print(json.dumps(item, indent=4, sort_keys=True))
                 nfound += 1
   shlog.normal("{} of {} items returned".format(nfound, nitems))


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    vaultdir = config.get("DEFAULT", "vaultdir", fallback="~/.vault")
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")

    if remote:
        # augment remote parser with a new subcommand
        inf_find_parser = parser.add_parser('inf_find', parents=[parent_parser], description=find_main.__doc__)
        inf_find_parser.set_defaults(func=find_main)
        # arguments will be attached to subcommand
        target_parser = inf_find_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--vaultdir', '-v',help='path to directory containing AWS logs (default: %(default)s)', default=vaultdir)
    target_parser.add_argument('--caseblind', '-c', help='caseblind compare (default: %(default)s)',action='store_true')
    target_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
    target_parser.add_argument('--date', '-da', help='anchor date, e.g 2021-4-30 (default: %(default)s)',
                                 type=(lambda x: date.fromisoformat(x)),
                                 default=date.today())
    target_parser.add_argument('--datedelta', '-dd',help='day offset from date  (e.g. -5:five days prior) (default: %(default)s)',type=int, default=0)
    target_parser.add_argument('searchglob',help='string to search for, in form of a glob. this goes at the end of the command')
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

   profile   = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
   loglevel  = config.get("FIND_BY_CONTENT", "loglevel",fallback="NORMAL")


   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use (default: %(default)s)')
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                       default=loglevel,
                       choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])


   parser = parser_builder(None, parser, config, False)
   args = parser.parse_args()
   shlog.basicConfig(level=args.loglevel)
   shlog.debug(args)
   find_main(args)

