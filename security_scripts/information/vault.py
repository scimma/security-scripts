#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

The command uses the shell "trailscraper", which provides
for incremental updates of the files. The command is
sensitive to a config file.

Options available via <command> --help
"""
import os
import boto3
import logging
import regex as re
from pathlib import Path
import multiprocessing as mp
from threading import Lock

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
    perc = round((iteration/total)*100, 2)
    bar = ('░'*19).replace('░','█',int(round(perc/5,0))) + '░'
    return str("{:.2f}".format(perc)).zfill(6) + '% [' + bar + ']'



def main(args):
   """
   Download Cloudtrail logs to the vault directory.

   A vault file is bushy directory tree that is stored under
   $HOME/.vault. teh leaves are (many jason) files, each
   covering a small slice of time. The files contain AWS event records.
   """
   # set up client
   boto3.setup_default_session(profile_name=args.profile)
   global client
   client = boto3.client('s3')

   # prep vault folder
   global total_keys
   full_vault = os.path.join(os.path.expanduser(args.vaultdir), 'logs/') # backwards compatibility
   Path(full_vault).mkdir(parents=True, exist_ok=True)
   # expected folder structure: "logs/Scimma-event-trail/AWSLogs/acct_id/CloudTrail/"

   # regex the bucket and prefix
   try:
       re_bucket = re.findall('(?<=s3:\/\/)(.*?)(?=\/)', args.bucket)[0]
       re_prefix = re.findall('([^\/]+$)', args.bucket)[0] + '/AWSLogs/' + str(args.accountid) + '/CloudTrail/'
   except IndexError:
       logging.info('error parsing bucket ' + args.bucket + ', s3://bucket/prefix format is expected')
       exit(0)

   logging.info('Building key dictionary...')

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
        client.download_file(keys['bucket'], keys['key'], keys['filepath'])


if __name__ == "__main__":

   import argparse 
   import configparser

   config = configparser.ConfigParser()
   config.read_file(open('defaults.cfg'))
   vaultdir = config.get("DOWNLOAD", "vaultdir", fallback="~/.vault")
   profile  = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
   accountid = config.get("DOWNLOAD", "accountid",fallback="585193511743")
   loglevel = config.get("DOWNLOAD", "loglevel",fallback="INFO")
   bucket   = config.get("DOWNLOAD", "bucket")
   
   
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--profile','-p',default=profile,help='aws profile to use')
   parser.add_argument('--debug'   ,'-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--loglevel','-l',help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)
   parser.add_argument('--vaultdir'     ,help='vault directory def:%s' % vaultdir, default=vaultdir)
   parser.add_argument('--bucket'       ,help='bucket with cloudtail logs', default=bucket)
   parser.add_argument('--accountid', help='AWS account id', default=accountid)

   args = parser.parse_args()
   logging.basicConfig(level=args.loglevel)

   main(args)


