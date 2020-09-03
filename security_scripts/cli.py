#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

The command uses the shell "trailscraper", which provides
for incremental updates of the files. The command is
sensitive to a config file.

Options available via <command> --help
"""
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
# from . import cfg  # relative-import the *package* containing the templates


def inf():
    """
    Information functions that allow for forensic investigations of AWS logs
    """
    print('inf launch')


def control():
    """
    Controlling functions that allow for influencing AWS account
    """
    print('control launch')


def catcher():
    import argparse
    import configparser
    import logging
    import sys

    config = configparser.ConfigParser()
    # config.read_file(pkg_resources.open_text(cfg, 'defaults.cfg'))

    # test, disable for deployment #
    import os
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "cfg/defaults.cfg"
    abs_file_path = os.path.join(script_dir, rel_path)
    config.read_file(open(abs_file_path))
    # test, disable for deployment #

    vaultdir = config.get("DOWNLOAD", "vaultdir", fallback="~/.vault")
    loglevel = config.get("DOWNLOAD", "loglevel", fallback="INFO")

    """Create command line arguments"""
    parent_parser = argparse.ArgumentParser(add_help=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parent_parser.add_argument('--vaultdir', '-v', default='~./vault')
    parent_parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)

    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    # inf parser
    inf_parser = subparsers.add_parser('inf', parents=[parent_parser], description=inf.__doc__)
    inf_parser.set_defaults(func=inf)

    # security parser
    control_parser = subparsers.add_parser('control', parents=[parent_parser], description=control.__doc__)
    control_parser.set_defaults(func=control)

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if not args.func or not args:  # there are no subfunctions
        parser.print_help()
        exit(1)
    logging.basicConfig(level=args.loglevel)

    args.func()



if __name__ == "__main__":
    catcher()


