#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

Options available via <command> --help
"""
import os
import boto3
import logging
from pathlib import Path
from threading import Lock
from security_scripts.information.lib import shlog

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

# enable process printing and counter
s_print_lock = Lock()
total_keys = 0
# define a global client to be defined later
client = None


def s_print(*a, **b):
    """Thread safe print function"""
    with s_print_lock:
        print(*a, **b)


def get_all_s3_objects(s3, **base_kwargs):
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield from response.get('Contents', [])
        if not response.get('IsTruncated'):  # At the end of the list?
            break
        continuation_token = response.get('NextContinuationToken')


def list_target_objects(source_folder: str):
    path = Path(source_folder)
    paths = []
    for file_path in path.rglob("*"):
        if file_path.is_dir():
            continue
        str_file_path = str(file_path)
        str_file_path = str_file_path.replace(f'{str(path)}/', "")
        paths.append(str_file_path)
    return paths


def progress_bar(iteration, total):
    """
    entertain the user with a simple yet exquisitely designed progress bar and %
    :param iteration:
    :param total:
    :return:
    """
    try:
        perc = round((iteration/total)*100, 2)
        bar = ('░'*19).replace('░','█',int(round(perc/5,0))) + '░'
        return str("{:.2f}".format(perc)).zfill(6) + '% [' + bar + ']'
    except ZeroDivisionError:
        # this happens in never versions of python. return nothing
        return ''





def vault_main(args):
   """Download Cloudtrail logs to the vault directory. Downloads are
   incremental -- previous downloads are not re-fetched or deleted.

   A vault file is bushy directory tree that is stored under
   $HOME/.vault. the leaves are (many json) files, each
   covering a small slice of time. The files contain AWS event records."""
   # set up client
   boto3.setup_default_session(profile_name=args.profile)
   global client
   client = boto3.client('s3')

   # prep vault folder
   global total_keys
   full_vault = os.path.join(os.path.expanduser(args.vaultdir), 'logs/') # backwards compatibility
   Path(full_vault).mkdir(parents=True, exist_ok=True)
   # expected folder structure: "logs/Scimma-event-trail/AWSLogs/acct_id/CloudTrail/"

   import regex as re
   # regex the bucket and prefix
   try:
       re_bucket = re.findall('(?<=s3:\/\/)(.*?)(?=\/)', args.bucket)[0]
       re_prefix = re.findall('([^\/]+$)', args.bucket)[0] + '/AWSLogs/' + str(args.accountid) + '/CloudTrail/'
   except IndexError:
       shlog.error('error parsing bucket ' + args.bucket + ', s3://bucket/prefix format is expected')
       exit(0)

   shlog.normal('Building key dictionary...')

   # init s3 and get bucket contents
   bucket_content = []
   keys = []
   dirs = []
   count = 0
   for item in get_all_s3_objects(boto3.client('s3'), Bucket=re_bucket, Prefix=re_prefix):
       key = item.get('Key')
       if key[-1] != '/':
           keys.append({'count':count,
                        'bucket':re_bucket,
                        'key':key,
                        'filepath':os.path.join(full_vault, key)})
       else:
           dirs.append(key)
       count += 1
   total_keys = len(keys)

   # prep high-level directories
   for d in dirs:
       dest_pathname = os.path.join(full_vault, d)
       if not os.path.exists(os.path.dirname(dest_pathname)):
           Path(dest_pathname).mkdir(parents=True, exist_ok=True)

   # download files in a multithread fashion
   import multiprocessing as mp
   pool = mp.Pool(min(mp.cpu_count(), len(keys)))  # number of workers
   pool.map(s3download, keys, chunksize=1)
   pool.close()


def s3download(keys):
    """
    download job to be multithreaded
    :param keys: keys dict passed by the pool command
    :return: None
    """
    global client # because multithreading can't stomach calls to clients defined within threads
    global total_keys
    dest_pathname = os.path.split(keys['filepath'])  # [0] is dir path, [1] is file name
    # prep landing folder
    if not os.path.exists(dest_pathname[0]):
        Path(dest_pathname[0]).mkdir(parents=True, exist_ok=True)
    if os.path.isfile(keys['filepath']):
        s_print(progress_bar(keys['count'], total_keys) + ' ' + dest_pathname[1] + ' already downloaded, skipping...', flush=True)
    else:
        s_print(progress_bar(keys['count'], total_keys) + ' Downloading ' + str(keys['filepath']), flush=True)
        try:
            client.download_file(keys['bucket'], keys['key'], keys['filepath'])
        except AttributeError:
            # global client could not be reached
            # this happens in newer experimental python builds 3.8+
            shlog.error('Your Python installation does not support global variables')
            shlog.error('Please use Python below 3.8.0')
            shlog.error('Could not download ' + dest_pathname[1])


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    bucket = config.get("DOWNLOAD", "bucket", fallback='s3://scimma-processes/Scimma-event-trail')
    vaultdir = config.get("DEFAULT", "vaultdir", fallback="~/.vault")
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")

    if remote:
        # augment remote parser with a new subcommand
        inf_vault_parser = parser.add_parser('inf_vault', parents=[parent_parser], description=vault_main.__doc__)
        inf_vault_parser.set_defaults(func=vault_main)
        # arguments will be attached to subcommand
        target_parser = inf_vault_parser
    else:
        # augments will be added to local parser
        target_parser = parser
    target_parser.add_argument('--bucket', '-b', help='bucket with cloudtail logs (default: %(default)s)',default=bucket)
    target_parser.add_argument('--vaultdir', '-v',help='path to directory containing AWS logs (default: %(default)s)',default=vaultdir)
    target_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
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

   profile  = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
   loglevel = config.get("DOWNLOAD", "loglevel",fallback="NORMAL")
   
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use (default: %(default)s)')
   parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                       default=loglevel,
                       choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])

   parser = parser_builder(None, parser, config, False)

   args = parser.parse_args()
   shlog.basicConfig(level=args.loglevel)



   vault_main(args)


