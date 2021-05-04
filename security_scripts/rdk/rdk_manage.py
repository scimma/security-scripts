#!/usr/bin/env python
"""
RDK manage.

Manage the deployments for SCIMMA.   

Options available via <command> --help

"""

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

   profile  = config.get("TAG_REPORT", "profile")
   loglevel = config.get("TAG_REPORT", "loglevel",fallback="NORMAL")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                       default=loglevel,
                       choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')

   parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   print (args)
   shlog.basicConfig(level=args.loglevel)

   main(args)

