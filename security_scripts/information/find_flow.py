from security_scripts.information.lib import shlog
from datetime import date,timedelta
import regex as re
import gzip
import time
import tabulate

from security_scripts.information.find_by_content import filter_template_paths_by_date_range


def  get_all_template_paths(args):
   """
   Return a globbed path to all event files for each  date.

   The template covers all AWS regions.
   e.g  logs/Scimma-event-trail/AWSLogs/acct_id/CloudTrail/*/2020/08/20/*.json.gz
   """
   from pathlib import Path
   import glob
   args.datepath = "logs/flow-logs/AWSLogs/" + args.accountid + "/vpcflowlogs/"
   root = os.path.join(args.vaultdir, args.datepath)
   root = Path(os.path.expanduser(root)) # gt rit of any laeding ~
   root = "{}".format(root)              # go figure have to make it a string
   dir_filter = os.path.join(root,'*/20[0-9][0-9]/[0-9][0-9]/[0-9][0-9]/')
   paths = {os.path.dirname(p)  for p in glob.glob(dir_filter)}  # all paths into  set
   paths = {p.replace(root,'') for p in paths}                   # reduce to unique site/y/m/d
   paths = {os.path.join(*p.split('/')[2:]) for p in  paths}     # strip off site
   #Now path is just the date component e.g 2020/08/22, one for each date in the store
   #Compose into full template
   paths  = [os.path.join(args.vaultdir,args.datepath,"*",p,"*.log.gz") for p in  paths]
   paths.sort()                                                  # assure oldset to recent
   return paths


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

    template_path = os.path.expanduser(template_path)
    list = []
    for path in glob.glob(template_path):
        # get stamp from file name
        # with gzip.open(path, 'rb') as f:
        filedate = re.findall('[^\/]+$', path)[0].split('_')[4]
        list.append("{} {}".format(filedate, path))
    list.sort()  # sort on date
    list = [l.split(" ") for l in list]
    if list != []:
        shlog.vverbose("first date, file available is {}".format(list[0]))
        shlog.vverbose("last  date, file available is {}".format(list[-1]))
    return [l[1] for l in list]


def render_dates(args, data):
    """replace unix number time with formatted time."""
    for d in data:
        d[10] = time.ctime(int(d[10]))
        d[11] = time.ctime(int(d[11]))
    return data

def render_protocols(args, data):
    """ replace prootocol number with protocoal name, for common protocols"""
    for d in data:
        if d[7] == '1'  : d[7] = 'icmp'
        if d[7] == '6'  : d[7] = 'tcp'
        if d[7] == '17' : d[7] = 'udp'
    return data

def render_services(args, data):
    """ replace service number with service name, for common services"""
    for d in data:
        for col in [5, 6]:
            if d[col] == '22'   : d[col] = 'ssh'
            if d[col] == '23'   : d[col] = 'telnet'
            if d[col] == '53'   : d[col] = 'domain'
            if d[col] == '80'   : d[col] = 'http'
            if d[col] == '88'   : d[col] = 'kreberos'
            if d[col] == '123'  : d[col] = 'ntp'
            if d[col] == '161'  : d[col] = 'snmp'
            if d[col] == '443'  : d[col] = 'https'
            if d[col] == '563'  : d[col] = 'nntps'
            if d[col] == '636'  : d[col] = 'ldaps'
            if d[col] == '992'  : d[col] = 'telnets'
    return data


def find_flow(args):
    all_template_paths = get_all_template_paths(args)
    filtered_template_paths = filter_template_paths_by_date_range(args, all_template_paths)
    all_data = []
    for template_path in filtered_template_paths:
      for file in time_ordered_event_archives(args, template_path):
       with gzip.open(file, 'rb') as f:
           data = f.read()
           data = data.split(b'\n')
           # clean
           # strip off possible blank lines at the end
           while not data[-1]: data.pop(-1)
           # break off into columns and grab header
           data = [d.split(b" ") for d in data]
           headers = data.pop(0)
           all_data = all_data + data

    # sort data into time ordered by begin time
    all_data = sorted(all_data, key=lambda all_data: all_data[10])

    # transform to more readable, if indicated
    if args.render_dates: data = render_dates(args, all_data)
    if args.render_protocols: data = render_protocols(args, all_data)
    if args.render_services: data = render_services(args, all_data)

    # display
    print(tabulate.tabulate(all_data, headers=headers))
    print('**, common protocols icmp:1, tcp:6, udp:17')

    pass


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    vaultdir = config.get("DEFAULT", "flowvault", fallback="~/.flow_vault")
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")

    if remote:
        # augment remote parser with a new subcommand
        inf_flow_parser = parser.add_parser('inf_flow', parents=[parent_parser], description=find_flow.__doc__)
        inf_flow_parser.set_defaults(func=find_flow)
        # arguments will be attached to subcommand
        target_parser = inf_flow_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--vaultdir', '-v',help='path to directory containing AWS logs (default: %(default)s)', default=vaultdir)
    target_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
    target_parser.add_argument('--render_dates', '-rd', help='render timestamps as localtime', default=False,
                        action='store_true')
    target_parser.add_argument('--render_protocols', '-rp', help='render protocol as text', default=False, action='store_true')
    target_parser.add_argument('--render_services', '-rs', help='render protocol as text', default=False, action='store_true')
    target_parser.add_argument('--date', '-da', help='anchor date, e.g 2021-4-30 (default: %(default)s)',
                                 type=(lambda x: date.fromisoformat(x)),
                                 default=date.today())
    target_parser.add_argument('--datedelta', '-dd',help='day offset from date  (e.g. -5:five days prior) (default: %(default)s)',type=int, default=0)
    return parser


if __name__ == "__main__":

    import argparse
    import configparser


    """get flow logs for a period"""
    from security_scripts.kli import env_control
    config = configparser.ConfigParser()
    import os
    rel_path = "defaults.cfg"
    cfg_sources = [rel_path,  # built-in config for fallback
                   os.path.expanduser(env_control())  # env value
                   ]
    config.read(cfg_sources)

    profile   = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
    loglevel  = config.get("FIND_BY_CONTENT", "loglevel" ,fallback="NORMAL")



    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--profile' ,'-p' ,default=profile ,help='aws profile to use (default: %(default)s)')
    parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                        default=loglevel,
                        choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])


    parser = parser_builder(None, parser, config, False)
    args = parser.parse_args()
    shlog.basicConfig(level=args.loglevel)
    shlog.debug(args)
    find_flow(args)

