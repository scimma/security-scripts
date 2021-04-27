from security_scripts.information.lib import shlog
from datetime import date,timedelta
import regex as re
import gzip
import time
import tabulate
import pandas as pd
import os
from netaddr import IPNetwork, IPAddress

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


def render_dates(args, df):
    """replace unix number time with formatted time."""
    df['start'] = pd.to_datetime(df['start'], unit='s')
    df['end'] = pd.to_datetime(df['end'], unit='s')
    return df

def render_protocols(args, df):
    """ replace prootocol number with protocoal name, for common protocols"""
    df.loc[df.protocol == '1', 'protocol'] = 'icmp'
    df.loc[df.protocol == '6', 'protocol'] = 'tcp'
    df.loc[df.protocol == '17', 'protocol'] = 'udp'
    return df

def render_services(args, df):
    """ replace service number with service name, for common services"""
    for col in ['srcport', 'dstport']:
        df[col][df[col] == '22'] = 'ssh'
        df[col][df[col] == '23'] = 'telnet'
        df[col][df[col] == '53'] = 'domain'
        df[col][df[col] == '80'] = 'http'
        df[col][df[col] == '8080'] = 'http'
        df[col][df[col] == '88'] = 'kerberos'
        df[col][df[col] == '123'] = 'ntp'
        df[col][df[col] == '161'] = 'snmp'
        df[col][df[col] == '443'] = 'https'
        df[col][df[col] == '563'] = 'nntps'
        df[col][df[col] == '636'] = 'ldaps'
        df[col][df[col] == '992'] = 'telnets'
    return df

def remove_unroutable(df):
    # create temp dataframe
    tempdf = pd.DataFrame()
    tempdf["src"] = df.apply(lambda row : is_unroutable(str(row["srcaddr"])), axis=1)
    tempdf["dst"] = df.apply(lambda row: is_unroutable(str(row["dstaddr"])), axis=1)

    # nuke rows with
    tempdf = tempdf[(tempdf['src'] == False) | (tempdf['dst'] == False)]
    df = df.drop(index=df.index.difference(tempdf.index))
    return df

def is_unroutable(ip):
    unro = False
    if IPAddress(ip) in IPNetwork('10.0.0.0/8') or \
            IPAddress(ip) in IPNetwork('172.16.0.0/12') or \
            IPAddress(ip) in IPNetwork('192.168.0.0/16'):
        unro = True
    return unro


def remove_custom(args, df):
    # create temp dataframe
    tempdf = pd.DataFrame()
    tempdf["src"] = df.apply(lambda row: in_custom_cids(args, str(row["srcaddr"])), axis=1)
    tempdf["dst"] = df.apply(lambda row: in_custom_cids(args, str(row["dstaddr"])), axis=1)
    # nuke rows where both are true
    tempdf = tempdf[(tempdf['src'] == False) | (tempdf['dst'] == False)]
    df = df.drop(index=df.index.difference(tempdf.index))
    return df

def in_custom_cids(args, ip):
    incidr = False
    for cidr in args.remove_custom.split(","):
        if IPAddress(ip) in IPNetwork(cidr):
            incidr = True
            break
    return incidr


def find_flow(args):
    """search flow logs by date"""
    all_template_paths = get_all_template_paths(args)
    filtered_template_paths = filter_template_paths_by_date_range(args, all_template_paths)
    all_data = []
    print_header = True
    for template_path in filtered_template_paths:
      for file in time_ordered_event_archives(args, template_path):
       with gzip.open(file, 'rb') as f:
           data = f.read()
           data = data.split(b'\n')
           # clean
           # strip off possible blank lines at the end
           while not data[-1]: data.pop(-1)
           # and NODATA entries
           data = list(filter(lambda a: not b'NODATA' in a, data))
           # break off into columns and grab header
           data = [d.split(b" ") for d in data]

           # fix bytes for presentation purposes
           for i in range(0, len(data)):
               for p in range(0, len(data[i])):
                   data[i][p] = data[i][p].decode("utf-8")

           headers = data.pop(0)
           # PANDAS MAGIC
           # allow pretty console print
           pd.set_option('display.max_columns', None)
           pd.set_option('display.expand_frame_repr', False)

           df = pd.DataFrame(data, columns=headers)

           # do handling here
           # transform to more readable, if indicated
           if args.render_dates: df = render_dates(args, df)
           if args.render_protocols: df = render_protocols(args, df)
           if args.render_services: df = render_services(args, df)
           if args.remove_unroutable: df = remove_unroutable(df)
           if args.remove_custom != '': df = remove_custom(args, df)

           if not print_header:
               headers = []
           try:
               print(tabulate.tabulate(df, showindex=False, headers=headers, tablefmt='plain', colalign='left'))
           except IndexError:
               # empty dataframe
               pass
           print_header = args.one_header

    # print('**, common protocols icmp:1, tcp:6, udp:17')

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
        inf_flow_parser = parser.add_parser('inf_find_flow', parents=[parent_parser], description=find_flow.__doc__)
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
    target_parser.add_argument('--remove_unroutable', '-ru', help='remove private ips from output', default=False,
                               action='store_true')
    target_parser.add_argument('--remove_custom', '-rc', help='remove custom CIDR ranges (comma-separated)', default='')
    target_parser.add_argument('--one_header', '-oh', help='repeat header only once', default=True,
                               action='store_false')
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

