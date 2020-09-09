#!/usr/bin/env python
"""
Update (or create) a vault directory populated with files
from Cloudtrail logs.

The command uses the shell "trailscraper", which provides
for incremental updates of the files. The command is
sensitive to a config file.

Options available via <command> --help
"""
import argparse


def inf_vault(args):
    """Build local event log vault"""
    from security_scripts.information import vault
    vault.main(args)


def inf_find(args):
    """Search logs in vault for a string"""
    from security_scripts.information import find_by_content
    find_by_content.main(args)


def inf_s3(args):
    """Print S3 storage resource on stdout"""
    from security_scripts.information import s3_report
    s3_report.main(args)


def inf_tag(args):
    """Check consistenty of AWS implementation with SCIMMA rules"""
    from security_scripts.information import tag_report
    tag_report.main(args)


def control_audit(args):
    """Run all available audits"""
    from security_scripts.controls import audit  # this doesn't work in terminal, only IDEs and in package form
    audit.all(args)


def control_red_button(args):
    """Deprivilege target role and stop all ec2 instances"""
    from security_scripts.controls import buttons
    buttons.depriv(args)
    buttons.ec2stop(args, False)


def control_green_button(args):
    """Reprivilege target role"""
    from security_scripts.controls import buttons
    buttons.priv(args)

def test_red_button(args):
    """Test deprivilege and ec2-stopping abilities"""
    from security_scripts.controls import tests
    tests.depriv(args)
    tests.ec2stop(args)


def test_green_button(args):
    """Test reprivileging abilities"""
    from security_scripts.controls import tests
    tests.priv(args)



def catcher():
    import configparser
    import logging
    import sys
    from datetime import date, timedelta

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
    dbfile = config.get("TAG_REPORT", "dbfile", fallback=":memory:")

    # argparse.ArgumentDefaultsHelpFormatter doesn't work...
    """Create command line arguments"""
    parent_parser = argparse.ArgumentParser(add_help=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parent_parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN (default: %(default)s)", default=loglevel)
    parent_parser.add_argument('--profile', '-p', default=profile, help='~/.aws/config profile to use (default: %(default)s)')
    parent_parser.add_argument('--role', '-r', default=target_role, help='target role for actions (default: %(default)s)')
    parent_parser.add_argument('--accountid', '-a', help='AWS account id to use for log and policy arns (default: %(default)s)', default=accountid)


    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    # vault parser
    inf_vault_parser = subparsers.add_parser('inf_vault', parents=[parent_parser], description=inf_vault.__doc__)
    inf_vault_parser.set_defaults(func=inf_vault)
    inf_vault_parser.add_argument('--bucket', '-b', help='bucket with cloudtail logs (default: :memory:)', default=bucket)
    inf_vault_parser.add_argument('--vaultdir', '-v', help='path to directory containing AWS logs (default: %(default)s)', default=vaultdir)

    # find parser
    inf_find_parser = subparsers.add_parser('inf_find', parents=[parent_parser], description=inf_find.__doc__)
    inf_find_parser.set_defaults(func=inf_find)
    inf_find_parser.add_argument('--vaultdir', '-v', help='path to directory containing AWS logs (default: %(default)s)', default=vaultdir)
    inf_find_parser.add_argument('--caseblind', '-c', help='caseblind compare (default: %(default)s)', action='store_true')
    inf_find_parser.add_argument('--date', '-da', help='anchor date, e.g 2021-4-30 (default: %(default)s)',
                                 type=(lambda x: date.fromisoformat(x)),
                                 default=date.today())
    inf_find_parser.add_argument('--datedelta', '-dd', help='day offset from date  (e.g. -5:five days prior) (default: %(default)s)', type=int, default=0)
    inf_find_parser.add_argument('searchglob', help='string to search for, in form of a glob. this goes at the end of the command')

    # s3 parser
    inf_s3_parser = subparsers.add_parser('inf_s3', parents=[parent_parser], description=inf_s3.__doc__)
    inf_s3_parser.set_defaults(func=inf_s3)

    # tag parser
    inf_tag_parser = subparsers.add_parser('inf_tag', parents=[parent_parser], description=inf_tag.__doc__)
    inf_tag_parser.set_defaults(func=inf_tag)
    inf_tag_parser.add_argument('--dbfile', '-df', help='database file to use (default: :memory:)', default=dbfile)
    inf_tag_parser.add_argument('--dump', '-du', help="dump data and quit, do not apply test (default: %(default)s)",
                                default=False, action='store_true')

    # audit parser
    control_audit_parser = subparsers.add_parser('control_audit', parents=[parent_parser], description=control_audit.__doc__)
    control_audit_parser.set_defaults(func=control_audit)

    # green button parser
    green_parser = subparsers.add_parser('control_green_button', parents=[parent_parser], description=control_green_button.__doc__)
    green_parser.set_defaults(func=control_green_button)

    # red button parser
    red_parser = subparsers.add_parser('control_red_button', parents=[parent_parser], description=control_red_button.__doc__)
    red_parser.set_defaults(func=control_red_button)

    # green button test
    test_green_parser = subparsers.add_parser('test_green_button', parents=[parent_parser], description=test_green_button.__doc__)
    test_green_parser.set_defaults(func=test_green_button)

    # red button test
    test_red_parser = subparsers.add_parser('test_red_button', parents=[parent_parser], description=test_red_button.__doc__)
    test_red_parser.set_defaults(func=test_red_button)


    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser_help(parser)
        sys.exit()

    if not args.func or not args:  # there are no subfunctions
        parser_help(parser)
        exit(1)
    logging.basicConfig(level=args.loglevel)

    args.datepath = "logs/Scimma-event-trail/AWSLogs/" + args.accountid + "/CloudTrail/"
    args.func(args)


def parser_help(parser):
    parser.print_help()
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)]
    for subparsers_action in subparsers_actions:
        # get all subparsers and print help
        for choice, subparser in subparsers_action.choices.items():
            print("\nArgument '{}':".format(choice))
            print('\t' + subparser.description)
            print("\tType 'sc {} -h' for use information".format(choice))


if __name__ == "__main__":
    catcher()


