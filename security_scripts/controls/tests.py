#!/usr/bin/env python
"""
Make requests to deprivilege a role, stop all ec2 units,
or reprivilege a role.

Options available via <command> --help
"""
import logging
from security_scripts.controls.audit import whoami as w
from security_scripts.information.lib import shlog
import boto3

def depriv(args):
    """
    RED button simulation that checks if the CLI user has correct permissions
    :return: None
    """
    shlog.normal('Simulating depriv...')
    shlog.normal('Attaching ReadOnlyAccess to ' + args.role)
    check(args)
    # exit(0)


def priv(args):
    """
    GREEN button simulation that checks if the CLI user has correct permissions
    :return: None
    """
    shlog.normal('Simulating priv...')
    shlog.normal('Attaching ProposedPoweruser and RoleManagementWithCondition to ' + args.role)
    check(args)


def check(args):
    """
    actual check
    :return:
    """
    me = w(args)
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('iam')
    response = client.simulate_principal_policy(
        PolicySourceArn=me,
        ActionNames=["iam:DetachRolePolicy", "iam:AttachRolePolicy"]
    )
    for result in response['EvaluationResults']:
        if result['EvalDecision'] == 'allowed':
            shlog.normal(result['EvalActionName'] + ' permission check ok!')
        else:
            shlog.normal('AWS reported ' + me + ' is not allowed to perform ' + result['EvalActionName'])


def ec2stop(args):
    """
    EC2 mass shutdown simulation
    :return: None
    """
    shlog.normal('Simulating ec2stop')
    me = w(args)
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('iam')
    response = client.simulate_principal_policy(
        PolicySourceArn=me,
        ActionNames=["ec2:StopInstances"]
    )
    for result in response['EvaluationResults']:
        if result['EvalDecision'] == 'allowed':
            shlog.normal('ec2:StopInstances permission check ok!')
        else:
            shlog.normal('AWS reported ' + me + ' is not allowed to perform ec2:StopInstances!')

    from security_scripts.controls.buttons import ec2stop as e
    e(args, True)


def test_red_button(args):
    """Test deprivilege and ec2-stopping abilities"""
    depriv(args)
    ec2stop(args)


def test_green_button(args):
    """Test reprivileging abilities"""
    priv(args)


def parser_builder(parent_parser, parser, config, remote=False):
    """Get a parser and return it with additional options
    :param parent_parser: top-level parser that will receive a subcommand; can be None if remote=False
    :param parser: (sub)parser in need of additional arguments
    :param config: ingested config file in config object format
    :param remote: whenever we
    :return: parser with amended options
    """
    target_role = config.get("DEFAULT", "role", fallback="scimma_power_user")
    accountid = config.get("DOWNLOAD", "accountid", fallback="585193511743")

    if remote:
        # green button parser
        green_test_parser = parser.add_parser('test_green_button', parents=[parent_parser], description=test_green_button.__doc__)
        green_test_parser.set_defaults(func=test_green_button)
        green_test_parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify (default: %(default)s)')
        green_test_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
        # red button parser
        red_test_parser = parser.add_parser('test_red_button', parents=[parent_parser], description=test_red_button.__doc__)
        red_test_parser.set_defaults(func=test_red_button)
        red_test_parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify (default: %(default)s)')
        red_test_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
    else:
        # augments will be added to local parser
        parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify ')
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

    profile = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
    loglevel = config.get("BUTTONS", "loglevel", fallback="NORMAL")

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--profile', '-p', default=profile, help='aws profile to use (default: %(default)s)')
    parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                        default=loglevel,
                        choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])

    # subcommands section
    parser.set_defaults(func=None)  # if none then there are  subfunctions
    subparsers = parser.add_subparsers(title="subcommands",
                                       description='valid subcommands',
                                       help='additional help')

    # Subcommand to check for installed dependencies
    depriv_parser = subparsers.add_parser('depriv', description=depriv.__doc__)
    depriv_parser.set_defaults(func=depriv)

    # Subcommand to target role policies
    priv_parser = subparsers.add_parser('priv', description=priv.__doc__)
    priv_parser.set_defaults(func=priv)

    # Subcommand to check for sufficient responder privileges
    ec2stop_parser = subparsers.add_parser('ec2stop', description=ec2stop.__doc__)
    ec2stop_parser.set_defaults(func=ec2stop)

    parser = parser_builder(None, parser, config, False)
    args = parser.parse_args()
    shlog.basicConfig(level=args.loglevel)


    args.session = boto3.Session(profile_name=args.profile)
    logging.getLogger('boto3').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('nose').setLevel(logging.ERROR)


    if not args.func:  # there are no subfunctions
        parser.print_help()
        exit(1)
    args.func(args)

