#!/usr/bin/env python
"""
Check consistenty of AWS implementation with SCIMMA rules.


Optons available via <command> --help
"""

import logging

       
def tag_main(args):
   """Check consistenty of AWS implementation with SCiMMA rules."""
   from security_scripts.information.lib import vanilla_utils
   from security_scripts.information.lib import tags

   q=vanilla_utils.Q(args.dbfile)

   tag_data = tags.Tags(args,"TAGS",q)
   tag_data.make_data()
   tag_data.clean_data()
   if args.dump:
      tag_data.print_data()
      exit()


   a = tags.Test_standard_tags(args, "Tagging Rule Check", q)
   #import pdb; pdb.set_trace()

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
        inf_tag_parser = parser.add_parser('inf_tag', parents=[parent_parser], description=tag_main.__doc__)
        inf_tag_parser.set_defaults(func=tag_main)
        # arguments will be attached to subcommand
        target_parser = inf_tag_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--dbfile', '-df', help='database file to use (default: %(default)s)', default=dbfile)
    target_parser.add_argument('--dump', '-du', help="dump data and quit, do not apply test (default: %(default)s)",
                                default=False, action='store_true')

    return parser
   

if __name__ == "__main__":

   import argparse
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("DEFAULT", "profile")
   loglevel = config.get("TAG_REPORT", "loglevel",fallback="NORMAL")

   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile', '-p', default=profile, help='aws profile to use (default: %(default)s)')
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN (default: %(default)s)", default=loglevel)

   parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   tag_main(args)

