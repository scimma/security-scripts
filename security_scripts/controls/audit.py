#!/usr/bin/env python
"""
Make requests to deprivilege a role, stop all ec2 units,
or reprivilege a role.

Options available via <command> --help
"""
import logging
import boto3

def dependencies(args):
    """
    perform a check for installed third-party applications
    :return: None
    """
    logging.info('Running dependencies check')
    import platform
    import os
    if platform.system() in ['Linux', 'Darwin']:
        # *nixes
        os.system("""# jq presence test function
                     if hash jq 2>/dev/null; then
                        echo "jq installed:  [  OK  ]"
                     else
                        echo "jq installed:  [FAILED]"
                        echo "please install jq"
                     fi
                     
                     if hash aws 2>/dev/null; then
                        echo "aws installed: [  OK  ]"
                     else
                        echo "aws installed: [FAILED]"
                        echo "please install aws"
                     fi
                  """)
    else:
        # windows; no other operating systems exist in the known universe
        os.system("""where jq>nul 2>&1 && echo jq installed:  [  OK  ] || echo jq installed:  [FAILED], please install jq
                  """)
        os.system("""where aws>nul 2>&1 && echo jq installed:  [  OK  ] || echo jq installed:  [FAILED], please install jq
                  """)


def policies(args):
    """
    list policies attached to a specified role
    :return: None
    """
    logging.info('Listing policies attached to ' + args.role)
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('iam')
    response = client.list_attached_role_policies(RoleName=args.role)
    for policy in response['AttachedPolicies']:
        logging.info(policy['PolicyName'] + '//' + policy['PolicyArn'])


def privileges(args):
    """
    check if the current CLI user has sufficient privileges
    :return: None
    """
    me = whoami(args)
    logging.info('Simulating needed administrative actions for ' + me)
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('iam')
    response = client.simulate_principal_policy(
        PolicySourceArn=me,
        ActionNames=["iam:DetachRolePolicy", "iam:AttachRolePolicy", "ec2:DescribeRegions", "ec2:StopInstances",
                     "ec2:ModifyInstanceAttribute", "sts:GetCallerIdentity"]
    )
    for result in response['EvaluationResults']:
        logging.info('Action: ' + result['EvalActionName'] + '// Simulation result: ' + result['EvalDecision'])

def repo(args):
    """
    repository checks script
    :return: None
    """
    logging.info('Checking repository status')
    import os
    os.system('git remote show origin')


def roles(args):
    """
    List existing AWS Roles
    :return: None
    """
    logging.info('Listing roles present in target AWS account')
    client = boto3.client('iam')
    response = client.list_roles()
    for role in response['Roles']:
        logging.info('Role: ' + role['RoleName'])


def whoami(args):
    """
    retrieve current user's ARN
    :return: String
    """
    logging.info('Retrieving caller identity')
    boto3.setup_default_session(profile_name=args.profile)
    client = boto3.client('sts')
    response = client.get_caller_identity()
    logging.info('AWS returned caller identity ' + response['Arn'])
    return response['Arn']


def all(args):
    """
    run all audits simultaneously
    :return: None
    """
    audits = ['dependencies(args)', 'policies(args)', 'privileges(args)', 'repo(args)', 'roles(args)', 'whoami(args)']
    for audit in audits:
        print('_________________')
        exec(audit)


if __name__ == "__main__":
    import argparse
    import configparser

    config = configparser.ConfigParser()
    config.read_file(open('defaults.cfg'))
    target_role  = config.get("DEFAULT", "role", fallback="scimma_power_user")
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
    dependencies_parser = subparsers.add_parser('dependencies', description=dependencies.__doc__)
    dependencies_parser.set_defaults(func=dependencies)

    # Subcommand to target role policies
    policies_parser = subparsers.add_parser('policies', description=policies.__doc__)
    policies_parser.set_defaults(func=policies)

    # Subcommand to check for sufficient responder privileges
    privileges_parser = subparsers.add_parser('privileges', description=privileges.__doc__)
    privileges_parser.set_defaults(func=privileges)

    # Subcommand to check repo state
    repo_parser = subparsers.add_parser('repo', description=repo.__doc__)
    repo_parser.set_defaults(func=repo)

    # Subcommand to list existing roles
    roles_parser = subparsers.add_parser('roles', description=roles.__doc__)
    roles_parser.set_defaults(func=roles)

    # Subcommand to retrieve current user's arn
    whoami_parser = subparsers.add_parser('whoami', description=whoami.__doc__)
    whoami_parser.set_defaults(func=whoami)

    # Subcommand to run all audits
    all_parser = subparsers.add_parser('all', description=all.__doc__)
    all_parser.set_defaults(func=all)


    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)


    logging.getLogger('boto3').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('nose').setLevel(logging.ERROR)

    if not args.func:  # there are no subfunctions
        parser.print_help()
        exit(1)
    args.func(args)

