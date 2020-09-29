#!/usr/bin/env python
"""
provides  variety  of checks and reports about
AWS usage for Information Security and AWS
Resource Management 


Optons available via <command> --help
"""

from security_scripts.information.lib import shlog

       
def main(args):
   from security_scripts.information.lib import vanilla_utils
   from security_scripts.information.lib import tags
   from security_scripts.information.lib import s3
   from security_scripts.information.lib import secrets
   from security_scripts.information.lib import certificates
   from security_scripts.information.lib import repos
   from security_scripts.information.lib import load_balancer
   
   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile)
   repos_acquire       = repos.Acquire(args,"repos",q)
   tag_acquire         = tags.Acquire(args,"TAGS",q)
   s3_acquire          = s3.Acquire(args, "s3", q)
   secret_acquire      = secrets.Acquire(args,"secrets",q)
   certificate_acquire = certificates.Acquire(args,"TAGS",q)
   load_balancer_acquire = load_balancer.Acquire(args,"load_balancer",q)
   # at this point data is in the relattion DB
   if args.dump:
      tag_acquire.print_data()
      s3_acquire.print_data()
      secret_acquire.print_data()
      certificate_acquire.print_data()
      repos_acquire.print_data()
      load_balancer_acquire.print_data()
      exit()

   # reporting actions are driven by instanitating the classes.
   tag_reports = tags.Report(args, "Tagging Rule Check", q)
   s3_reports=s3.Report(args, "s3", q)
   secret_reports = secrets.Report(args,"secrets",q)
   cert_reports = certificates.Report(args, "Certificates", q)
   repo_reports = repos.Report(args, "repos", q)
   x = load_balancer.Report(args, "load_balancers", q)


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
        inf_report_parser = parser.add_parser('inf_report', parents=[parent_parser], description=rep_main.__doc__)
        inf_report_parser.set_defaults(func=main)
        # arguments will be attached to subcommand
        target_parser = inf_report_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--dbfile', help='database file to use (default: %(default)s)', default=dbfile)
    target_parser.add_argument('--dump', help="dump data and quit, do not apply test (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--listonly', help="list tests and quit (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--only', help="only run reports matching glob (default: %(default)s)", default="*")
    target_parser.add_argument('--bare', help="print bare report, no wrap, no format (default: %(default)s)", default=False, action='store_true')
    return parser
   
if __name__ == "__main__":

   import argparse 
   import configparser

   """ get defaults from configuration system"""
   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   profile  = config.get("TAG_REPORT", "profile")
   loglevel = config.get("TAG_REPORT", "loglevel",fallback="NORMAL")
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--loglevel', '-l', help=shlog.helptext, default="NORMAL")
   parser.add_argument('--profile','-p',default=profile,
             help='aws profile to use')

   parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   print (args)
   shlog.basicConfig(level=args.loglevel)

   main(args)
