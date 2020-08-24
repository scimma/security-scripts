#!/usr/bin/env python
"""
Search the cloudtrail vault for strings
with the value given by searchglob.

Perform caseblind search if indicated.
TUncate matched string if indicated.

Options available via <command> --help
"""

import logging
import json
import fnmatch

class Cmp:
   """
    make a optionally case blind comparistio of two strings using a glob

    """
   def __init__(self, args):
        self.caseblind     = args.caseblind
        self.searchglob    = args.searchglob
        if self.caseblind: self.searchglob.upper()
        
   def match(self, value):
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
    """return a list of key, value pairs where value matches valuematch
   
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
                    # no match, let it go
                    logging.debug("skipping: %s", v)
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
                    logging.debug("skipping: %s", item)
        return arr

    results = match(obj, arr, valuematch, c)
    return results

def time_ordered_events(args):
   """
   Return  a list of [date, path] pairs, sorted by increasing date.
   
   Construct the list based on files in the vault, considering only
   the first timestanp in the file holding th evnets. Given the vault
   files are small timeslices, this should hlpe produce a event strean
   that is nearly time ordered.
   """
   import os
   from pathlib import Path
   import gzip
   
   list = []
   for path in Path(os.path.expanduser(args.vaultdir)).rglob('*.json.gz'):
      with gzip.open(path.absolute(), 'rb') as f:
         data = json.loads(f.read())
         list.append ("{} {}".format(data["Records"][0]["eventTime"],  path.absolute()))
   list.sort()
   list = [l.split(" ") for l in list]
   logging.debug("first date, file available is {}".format(list[0] ))
   logging.debug("last  date, file available is {}".format(list[-1]))
                                                          
   return list


def main(args):
   """
   Dump cloudtail json event records from the vault having a
   some value matching the globstring.

   A vault file is a dictionary of "Records" containing an array
   of json objects, One json object per cloudtrail event.
   There are a large variety of events, each with a
   different json schema.
   """
   import glob
   import os
   from pathlib import Path
   import gzip

   c = Cmp(args)
   if not any(ext in args.searchglob for ext in ["*", "?"]):
       logging.warning(args.searchglob + " does not have an * or ?")

   for date, path in time_ordered_events(args):
      with gzip.open(path, 'rb') as f:
           data = json.loads(f.read())
           for item in data['Records']:
              result = find_string(item, args.searchglob, c)
              if result :
                 print(json.dumps(item, indent=4, sort_keys=True))
   
if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   vaultdir  = config.get("FIND_BY_CONTENT", "vaultdir", fallback="~/.trailscraper")
   profile   = config.get("DEFAULT", "profile", fallback="default")
   loglevel  = config.get("FIND_BY_CONTENT", "loglevel",fallback="INFO")

   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help="Level for reporting e.r DEBUG, INFO, WARN", default=loglevel)
   parser.add_argument('--vaultdir'     ,help='vault directory def:%s' % vaultdir, default=vaultdir)
   parser.add_argument('--caseblind'     ,help='caseblind compare', action='store_true')
   parser.add_argument('searchglob'     ,help='string to search for, in form of a glob')

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)
   logging.debug(args)
   main(args)

