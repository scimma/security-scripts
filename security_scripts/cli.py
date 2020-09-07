#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

The command uses the shell "trailscraper", which provides
for incremental updates of the files. The command is
sensitive to a config file.

Options available via <command> --help
"""


def inf_vault(args):
    """
    Build local event log vault
    """
    from security_scripts.information import vault
    vault.main(args)


def inf_find():
    """
    Information functions that allow for forensic investigations of AWS logs
    """
    print('inf vault')


def inf_v():
    """
    Information functions that allow for forensic investigations of AWS logs
    """
    # todo: s3, tags
    print('inf vault')


def control(args):
    """
    Controlling functions that allow for influencing AWS account
    """
    print('control launch')


def control_audit(args):
    """
    Run all available audits
    """
    from security_scripts.controls import audit  # this doesn't work in terminal, only IDEs and in package form
    audit.all(args)


def control_red_button(args):
    """
    Deprivilege target role and stop all ec2 instances
    """
    from security_scripts.controls import buttons
    buttons.depriv(args)
    buttons.ec2stop(args, False)


def control_green_button(args):
    """
    Reprivilege target role
    """
    from security_scripts.controls import buttons
    buttons.priv(args)



def catcher():
    import argparse
    import configparser
    import logging
    import sys

    config = configparser.ConfigParser()

    # proven to work both in package and unpacked form
    import os
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "cfg/defaults.cfg"
    abs_file_path = os.path.join(script_dir, rel_path)
    config.read_file(open(abs_file_path))

    vaultdir = config.get("DEFAULT", "vaultdir", fallback="~/.vault")
    loglevel = config.get("DEFAULT", "loglevel", fallback="INFO")
    target_role = config.get("DEFAULT", "role", fallback="scimma_power_user")
    profile = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
    bucket = config.get("DOWNLOAD", "bucket", fallback='s3://scimma-processes/Scimma-event-trail')
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")


    """Create command line arguments"""
    parent_parser = argparse.ArgumentParser(add_help=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parent_parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)
    parent_parser.add_argument('--profile', '-p', default=profile, help='~/.aws/config profile to use')
    parent_parser.add_argument('--role', '-r', default=target_role, help='target role for actions')


    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    # vault parser
    inf_vault_parser = subparsers.add_parser('inf_vault', parents=[parent_parser], description=inf_vault.__doc__)
    inf_vault_parser.set_defaults(func=inf_vault)
    inf_vault_parser.add_argument('--bucket', '-b', help='bucket with cloudtail logs', default=bucket)
    inf_vault_parser.add_argument('--vaultdir', '-v', help='path to directory containing AWS logs', default=vaultdir)
    inf_vault_parser.add_argument('--accountid', '-a', help='AWS account id', default=accountid)

    # audit parser
    control_audit_parser = subparsers.add_parser('control_audit', parents=[parent_parser], description=control_audit.__doc__)
    control_audit_parser.set_defaults(func=control_audit)

    # green button parser
    green_parser = subparsers.add_parser('control_green_button', parents=[parent_parser], description=control_green_button.__doc__)
    green_parser.set_defaults(func=control_green_button)


    # red button parser
    red_parser = subparsers.add_parser('control_red_button', parents=[parent_parser], description=control_red_button.__doc__)
    red_parser.set_defaults(func=control_red_button)


    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if not args.func or not args:  # there are no subfunctions
        parser.print_help()
        exit(1)
    logging.basicConfig(level=args.loglevel)

    args.func(args)


if __name__ == "__main__":
    catcher()


