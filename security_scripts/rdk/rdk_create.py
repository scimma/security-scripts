#!/usr/bin/env python

"""
Create a new rule using  our coding conventions.

Conventions:
- Populate parameters.json with default tags.
- Select the default code environment.
- Provide an initial list of CI's
    - Show a list of sample CI's consistent with cipattern argument
    - Accept interactive comma-separated list of CI's
    - Construct a list of CIs within the generated rule.
    - Make a .json sample CI json file for each CI to support unit tests.

Options available via <command> --help

"""
import shlog
import os
import json


def execute_or_not(args, cmd):
    if not args.dry_run:
        shlog.normal("executing: {}".format(cmd))
        status = os.system(cmd)
        shlog.normal("command status:{}".format(status))
        if status:
            exit(status)
    else:
        shlog.normal("would have executed: \n {}".format(cmd))


def main(args):
    "perform (or dry run) the rdk create"

    if os.path.isdir(args.rulename):
        shlog.error("Exiting: {} is an existing rule".format(args.rulename))
        exit(1)
    # Specify the default taglist in plain python..
    default_json_tag_list = '''
    [
    {"Key" : "Criticality","Value" : "Development"},
    {"Key" : "Service"    ,"Value" : "OpSec"}
    ]
    '''
    # reformat to RDK's needs
    # - rdk demands a double encoded string.
    # - change to binary to remove white space, then double encode.
    default_json_tag_list = json.loads(default_json_tag_list)
    default_json_tag_list = json.dumps(default_json_tag_list)
    default_json_tag_list = json.dumps(default_json_tag_list)
    shlog.normal("setting default tags:{}".format(default_json_tag_list))

    #
    # Collect the CI's needed for the rule
    #
    cmd = '''rdk sample-ci sas 2>&1 | tr , "\\n" | grep -i '{}' '''.format(args.cipattern)
    status = os.system(cmd)
    shlog.normal(status)
    cis = input("Enter comma separated CI(s)>")
    ci_create_option = "-r {}".format(cis)

    # actually create the project.                                )
    cmd = "rdk create {} -R python3.6  --tags {}  {}".format(args.rulename, default_json_tag_list, ci_create_option)
    execute_or_not(args, cmd)

    # dump a sample ci in the project directory
    for ci in cis.split(","):
        cmd = "cd {}; rdk sample-ci {} > {}.json".format(args.rulename, ci, ci)
        execute_or_not(args, cmd)


if __name__ == "__main__":

    import argparse
    import configparser

    # get defaults from configuration system
    # From security_scripts.kli import env_control
    config = configparser.ConfigParser()
    rel_path = "../cfg/defaults.cfg"
    cfg_sources = [rel_path,  # built-in config for fallback
                   os.path.expanduser("$HOME/.scimma")  # env value
                   ]
    config.read(cfg_sources)
    profile  = config.get("RDK", "profile")
    loglevel = config.get("RDK", "loglevel",fallback="NORMAL")
    #loglevel = "NORMAL"
    #profile = "scimma-uiuc-aws-admin"
    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--loglevel', '-l',
                        help="Level for reporting e.g. NORMAL, VERBOSE, DEBUG (default: %(default)s)",
                        default=loglevel,
                        choices=["NONE", "NORMAL", "DOTS", "WARN", "ERROR", "VERBOSE", "VVERBOSE", "DEBUG"])
    parser.add_argument('--dry-run', '-n', default=False, action='store_true',
                        help="dry run just show what would be done")

    parser.add_argument('rulename',
                        help='name of rule to create')
    parser.add_argument('cipattern',
                        help='grep friendly pattern to show CIs')
    # parser = parser_builder(None, parser, config, False)

    args = parser.parse_args()
    shlog.basicConfig(level=args.loglevel)
    shlog.debug("{}".format(args))
    main(args)
