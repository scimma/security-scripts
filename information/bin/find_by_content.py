#!/usr/bin/env python
"""
Search the cloudtrail vault for strings
with the value given by searchglob.


Optons available via <command> --help
"""

import logging
import json
       
def extract_value(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def find_string(obj, valuematch,truncate=90):
    """return a list of key, value pairs where value matches valuematch
   
       Valuematch can be specifies as a glob style "wildcard"
       truncate any string to indicated length.
    """
    import fnmatch
    import copy
    arr = []
    context = []


    def match(obj, arr, valuematch, truncate):
        """Recursively search for values"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    match(v, arr, valuematch,  truncate )
                elif type(v) == type("") and fnmatch.fnmatch(v,valuematch):
                    arr.append([type(v),k,v[0:truncate]])
                else: #don;t return binary objects or failed to find.
                    pass
        elif isinstance(obj, list):
            for item in obj:
                match(item, arr, valuematch, truncate)
        return arr

    results = match(obj, arr, valuematch, truncate)
    return results



def main(args):
   """
   Dump cloudtail json event recordsfrom the vault having a
   some value matching the globstring.

   A vault file is a dictionary of "Records" containing an array
   of json objects, One json object per cloudtrail event.
   There are a large variety of events, each with a
   different json schema.
   """
   import glob
   import os 

   if not any(ext in args.searchglob for ext in ["*", "?"]):
       logging.warning(args.searchglob + " does not have an * or ?")
           
   for vfile in glob.glob(os.path.join(args.vaultdir,"*.json")):
       logging.info("searching " + vfile)
       
       with open(vfile,'r') as f:
           data = json.loads(f.read())
           for item in data['Records']:
               result = find_string(item, args.searchglob)
               if result : 
                   print(json.dumps(item, indent=4, sort_keys=True))
   

if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   vaultdir = config.get("DEFAULT", "vault", fallback="./vault")
   profile  = config.get("DEFAULT", "profile", fallback="sciimma-aws-admin")
   loglevel = config.get("DEFAULT", "loglevel",fallback="INFO")
 
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help="Level for  reporning e.r DEBUG, INFO, WARN", default="INFO")
   parser.add_argument('--vaultdir'     ,help='vault directory def:%s' % vaultdir, default=vaultdir)
   parser.add_argument('searchglob'     ,help='string to search for, in form of a glob')

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   main(args)

