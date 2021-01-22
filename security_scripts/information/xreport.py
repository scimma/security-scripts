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
   """Run reports pulling in existing infrastructure and mapping them to services"""
   from security_scripts.information.lib import vanilla_utils
   from security_scripts.information.lib import xs3
   from security_scripts.information.lib import xtags
   from security_scripts.information.lib import L0A
   from security_scripts.information.lib import L0A_L0B
   from security_scripts.information.lib import tag_counter
   from security_scripts.information.lib import untagged_lister
   from security_scripts.information.lib import L1_L2
   from security_scripts.information.lib import L0B_L1
   from security_scripts.information.lib import L2_L3

   # decode full path to dbfile so imports from other directories don't get confused
   if args.dbfile != ':memory:':
       args.dbfile = os.path.abspath(args.dbfile)

   shlog.verbose(args)
   shlog.verbose("only tests matching %s will be considered",(args.only))
   q=vanilla_utils.Q(args.dbfile, args.flush)

   # dict structure: lvl name: [import name, priority]
   xreports_dict = {'L0A': ['L0A', 1],
                    'L0B': ['L0A_L0B', 2],
                    'L1':  ['L0B_L1', 3],
                    'L2':  ['L1_L2', 4],
                    'L3':  ['L2_L3', 5]}

   if args.start not in xreports_dict.keys():
       shlog.normal('illegal start parameter: {}'.format(args.start))
       exit(0)

   if args.end not in xreports_dict.keys():
       shlog.normal('illegal end parameter: {}'.format(args.start))
       exit(0)

   for x in xreports_dict:
       # compare x's priority to arg's priority
       if xreports_dict[x][1] >= xreports_dict[args.start][1] and xreports_dict[x][1] <= xreports_dict[args.end][1]:
           exec_string = '{}.Acquire(args, "{}", q)'.format(xreports_dict[x][0], xreports_dict[x][0])
           exec(exec_string)

   # there's more stuff down there, think about implementing it
   exit(0)
   s3_acquire = xs3.Acquire(args, "s3", q)
   tags_acquire = xtags.Acquire(args, "tags", q)
   tag_c_acquire       = tag_counter.Acquire(args, "TAG_COUNTER",q)
   untagged = untagged_lister.Acquire(args, "UNTAGGED_LISTER", q)

   # at this point data is in the relattion DB
   if args.dump:
      # tag_acquire.print_data()
      # s3_acquire.print_data()
      # secret_acquire.print_data()
      # certificate_acquire.print_data()
      # load_balancer_acquire.print_data()
      # repos_acquire.print_data()
      # instances_acquire.print_data()
      exit()

   # reporting actions are driven by instanitating the classes.
   tag_reports = xtags.Report(args, "Tagging Rule Check", q)
   tag_c_report = tag_counter.Report(args, "Tagging Count Check", q)
   untagged_report = untagged_lister.Report(args, "Untagged Resources", q)
   exit()
   # s3_reports=s3.Report(args, "s3", q)
   # secret_reports = secrets.Report(args,"secrets",q)
   # cert_reports = certificates.Report(args, "Certificates", q)
   # load_balancer_reports = load_balancer.Report(args, "load_balancers", q)
   # repo_reports = repos.Report(args, "repos", q)
   # instances_reports = instances.Report(args, "Tagging Rule Check", q)


   # assets.Acquire(args,"assets", q)
   # assets.Report(args,"assets",q)

def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    dbfile = config.get("TAG_REPORT", "dbfile", fallback=":memory:")
    start = config.get("TAG_REPORT", "start", fallback="L0A")
    end = config.get("TAG_REPORT", "end", fallback="L3")
    tag = config.get("TAG_REPORT", "tag", fallback="Service")

    if remote:
        # augment remote parser with a new subcommand
        inf_report_parser = parser.add_parser('x_report', parents=[parent_parser], description=main.__doc__)
        inf_report_parser.set_defaults(func=main)
        # arguments will be attached to subcommand
        target_parser = inf_report_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--dbfile', help='database file to use (default: %(default)s)', default=dbfile)
    target_parser.add_argument('--dump', help="dump data and quit, do not apply test (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--flush', '-f', help='flush database during processing (default: %(default)s)', default=False, action='store_true')
    target_parser.add_argument('--listonly', help="list tests and quit (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--only', help="only run reports matching glob (default: %(default)s)", default="*")
    target_parser.add_argument('--bare', help="print bare report, no wrap, no format (default: %(default)s)", default=False, action='store_true')
    target_parser.add_argument('--start', '-s', help="information product level to start processing from (inclusive) (default: %(default)s)"
                                                     " available options: L0A, L0B, L1, L2, L3", default=start)
    target_parser.add_argument('--end', '-e', help="information product level to stop processing (inclusive) (default: %(default)s)"
                                    " available options: L0A, L0B, L1, L2, L3", default=end)
    target_parser.add_argument('--despace', '-ds', help="remove spaces from tags; fixes ungrouped objects in L2->L3 (default: %(default)s)",
                               default=False, action='store_true')
    target_parser.add_argument('--tag', '-t', help="tag to use as a galaxy former at L3 (default: %(default)s)", default=tag)
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

