#!/usr/bin/env python
"""
Make requests to deprivilege a role, stop all ec2 units,
or reprivilege a role.

Options available via <command> --help
"""
import logging
import boto3

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)


def detacher(args, role):
    """
    Loop through all policies attached to a role and detach them
    :return:
    """
    # get attached policies and detach them in a loop
    for policy in role.attached_policies.all():
        logging.info('Detaching policy ' + policy.arn + ' from role ' + args.role)
        response = role.detach_policy(PolicyArn=policy.arn)
        logging.debug(response)


def depriv(args):
    """
    Make a request to deprivilege the target role to no permissions
    :return: None
    """
    boto3.setup_default_session(profile_name=args.profile)
    iam = boto3.resource('iam')
    role = iam.Role(args.role)
    detacher(args, role)
    # attach read-only
    logging.info('Attaching ReadOnlyAccess to ' + args.role)
    response = role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/ReadOnlyAccess')
    logging.debug(response)


def priv(args):
    """
    Make a request to elevate the target role to ProposedPoweruser
    :return: None
    """
    boto3.setup_default_session(profile_name=args.profile)
    iam = boto3.resource('iam')
    role = iam.Role(args.role)
    detacher(args, role)
    # attach read-only
    logging.info('Attaching ProposedPoweruser and RoleManagementWithCondition to ' + args.role)
    response = role.attach_policy(PolicyArn='arn:aws:iam::' + args.accountid + ':policy/ProposedPoweruser')
    logging.debug(response)
    response = role.attach_policy(PolicyArn='arn:aws:iam::' + args.accountid + ':policy/RoleManagementWithCondition')
    logging.debug(response)


def ec2stop(args, dryrun=False):
    """
    Make a request to stop all ec2 instances
    :return:
    """
    from botocore.exceptions import ClientError
    from security_scripts.information.lib import aws_utils as au # only works in plugin and IDE
    args.session = boto3.Session(profile_name=args.profile)
    regions = au.decribe_regions_df(args) # use for deployment
    # regions = {'RegionName':['us-east-2']} # test mode
    for region in regions['RegionName']:
        logging.info('Stopping region ' + region)
        # init connection to region and get instances there
        client = boto3.client('ec2', region_name=region)
        response = client.describe_instances()['Reservations']
        # go through intance ids
        for inst in response:
            # ...and allow termination...
            instance = inst['Instances'][0]['InstanceId']
            logging.info('Allowing API termination for instance ' + instance + ' in region ' + region)
            response = client.modify_instance_attribute(
                InstanceId=instance,
                DisableApiTermination={'Value': False}
            )
            logging.debug(response)
            # ...and perform halt
            logging.info('Stopping instance ' + instance + ' in region ' + region)
            try:
                response = client.stop_instances(
                    InstanceIds=[instance],
                    DryRun=dryrun,
                    Force=True
                )
            except ClientError as ce:
                if dryrun:
                    # client error is expected when simulating
                    logging.info('Stop simulation succeeded with code:')
                    logging.info(ce)
                else:
                    # we might actually want to catch real exceptions
                    raise ClientError
    pass


def control_green_button(args):
    """Reprivilege target role"""
    priv(args)


def control_red_button(args):
    """Deprivilege target role and stop all ec2 instances"""
    depriv(args)
    ec2stop(args, False)


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
        green_parser = parser.add_parser('control_green_button', parents=[parent_parser], description=control_green_button.__doc__)
        green_parser.set_defaults(func=control_green_button)
        green_parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify  (default: %(default)s)')
        green_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
        # red button parser
        red_parser = parser.add_parser('control_red_button', parents=[parent_parser], description=control_red_button.__doc__)
        red_parser.set_defaults(func=control_red_button)
        red_parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify  (default: %(default)s)')
        red_parser.add_argument('--accountid', help='AWS account id (default: %(default)s)', default=accountid)
    else:
        # augments will be added to local parser
        parser.add_argument('--role', '-r', default=target_role, help='AWS role to modify  (default: %(default)s)')
    return parser


if __name__ == "__main__":
    import argparse
    import configparser

    config = configparser.ConfigParser()
    config.read_file(open('defaults.cfg'))
    profile = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")
    loglevel = config.get("BUTTONS", "loglevel", fallback="INFO")

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--profile', '-p', default=profile, help='aws profile to use (default: %(default)s)')
    parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN (default: %(default)s)", default=loglevel)

    # subcommands section
    parser.set_defaults(func=None)  # if none then there are  subfunctions
    subparsers = parser.add_subparsers(title="subcommands",
                                            description='valid subcommands',
                                            help='additional help')
    # Subcommand to deprivilege
    depriv_parser = subparsers.add_parser('depriv', description=depriv.__doc__)
    depriv_parser.set_defaults(func=depriv)

    # Subcommand to privilege
    priv_parser = subparsers.add_parser('priv', description=priv.__doc__)
    priv_parser.set_defaults(func=priv)

    # Subcommand to stop ec2 instances
    ec2_parser = subparsers.add_parser('ec2stop', description=ec2stop.__doc__)
    ec2_parser.set_defaults(func=ec2stop)

    parser = parser_builder(None, parser, config, False)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)


    # args.session = boto3.Session(profile_name=args.profile)

    if not args.func:  # there are no subfunctions
        parser.print_help()
        exit(1)
    args.func(args)

