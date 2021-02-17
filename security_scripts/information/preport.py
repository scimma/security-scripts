#!/usr/bin/env python
"""
provides  variety  of checks and reports about
AWS usage for Information Security and AWS
Resource Management 


Optons available via <command> --help
"""

from security_scripts.information.lib import shlog
import os

       
def main(args):
   """visualize IAM entities and policies attached to them
        x_report needs to be run first"""
   from security_scripts.information.lib import vanilla_utils
   from security_scripts.information.lib import L1_L2
   from security_scripts.information.lib import Liam

   # decode full path to dbfile so imports from other directories don't get confused
   if args.dbfile != ':memory:':
       args.dbfile = os.path.abspath(args.dbfile)

   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile, args.flush)

   # switch in custom to_self and to_others
   L1_replacer()

   # run L1_L2
   L1_L2.Acquire(args, "L1_L2", q)

   # cluster by type (label minus name minus /n
   Liam.Acquire(args, "Liam", q)

   exit(0)



def L1_replacer():
    from security_scripts.information import L1_preport
    l1dir = os.getcwd() + "/report_files/L1/"
    shlog.verbose("Overwriting L1 files")
    with open(l1dir + 'to_self.json', 'w') as file:
        file.write(L1_preport.t_self)
    with open(l1dir + 'to_others.json', 'w') as file:
        file.write(L1_preport.t_others)


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    dbfile = config.get("TAG_REPORT", "dbfile", fallback=":memory:")

    if remote:
        # augment remote parser with a new subcommand
        inf_report_parser = parser.add_parser('p_report', parents=[parent_parser], description=main.__doc__)
        inf_report_parser.set_defaults(func=main)
        # arguments will be attached to subcommand
        target_parser = inf_report_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--dbfile', help='database file to use (default: %(default)s)', default=dbfile)
    target_parser.add_argument('--flush', '-f', help='flush database during processing (default: %(default)s)', default=False, action='store_true')
    target_parser.add_argument('--dump', help="dump data and quit, do not apply test (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--listonly', help="list tests and quit (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--only', help="only run reports matching glob (default: %(default)s)", default="*")
    target_parser.add_argument('--bare', help="print bare report, no wrap, no format (default: %(default)s)", default=False, action='store_true')
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

