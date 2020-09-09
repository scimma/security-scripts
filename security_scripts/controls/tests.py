#!/usr/bin/env python
"""
Make requests to deprivilege a role, stop all ec2 units,
or reprivilege a role.

Options available via <command> --help
"""
import logging
from security_scripts.controls.audit import whoami as w
import boto3

def depriv(args):
    """
    RED button simulation that checks if the CLI user has correct permissions
    :return: None
    """
    logging.info('Simulating depriv...')
    logging.info('Attaching ReadOnlyAccess to ' + args.role)
    check(args)


def priv(args):
    """
    GREEN button simulation that checks if the CLI user has correct permissions
    :return: None
    """
    logging.info('Simulating priv...')
    logging.info('Attaching ProposedPoweruser and RoleManagementWithCondition to ' + args.role)
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
            logging.info(result['EvalActionName'] + ' permission check ok!')
        else:
            logging.info('AWS reported ' + me + ' is not allowed to perform ' + result['EvalActionName'])


def ec2stop(args):
    """
    EC2 mass shutdown simulation
    :return: None
    """
    logging.info('Simulating ec2stop')
    me = w(args)
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('iam')
    response = client.simulate_principal_policy(
        PolicySourceArn=me,
        ActionNames=["ec2:StopInstances"]
    )
    for result in response['EvaluationResults']:
        if result['EvalDecision'] == 'allowed':
            logging.info('ec2:StopInstances permission check ok!')
        else:
            logging.info('AWS reported ' + me + ' is not allowed to perform ec2:StopInstances!')

    from security_scripts.controls.buttons import ec2stop as e
    e(args, True)



if __name__ == "__main__":
    import argparse
    import configparser

    config = configparser.ConfigParser()
    config.read_file(open('defaults.cfg'))
    target_role = config.get("DEFAULT", "role", fallback="scimma_power_user")
    profile = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
    loglevel = config.get("BUTTONS", "loglevel", fallback="INFO")

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--debug', '-d', help='print debug info', default=False, action='store_true')
    parser.add_argument('--profile', '-p', default=profile, help='aws profile to use')
    parser.add_argument('--role', '-r', default=target_role, help='CLI profile to use')
    parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN", default=loglevel)

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

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)


    args.session = boto3.Session(profile_name=args.profile)
    logging.getLogger('boto3').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('nose').setLevel(logging.ERROR)


    if not args.func:  # there are no subfunctions
        parser.print_help()
        exit(1)
    args.func(args)

