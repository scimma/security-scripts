import argparse
import logging

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


def env_control():
    import platform
    import os
    var = 'SCIMMA_SECURITY_CFG'
    val = os.environ.get(var)
    if val:
        print('Reding custom config file locaiton from $' + var + ' as ' + val)
        return val
    else:
        if platform.system() in ['Linux', 'Darwin']:
            # *nixes
            val = '~/.scimma-security.cfg'
            with open(os.path.expanduser("~/.bash_profile"), "a") as outfile:
                outfile.write("export {0}={1}".format(var, val))
                # pass
            with open(os.path.expanduser("~/.zshenv"), "a") as outfile:
                # pass
                outfile.write("export {0}={1}".format(var, val))
            print('$' + var + ' written to ~/.bash_profile and ~/.zshenv as ' + val)
        else:
            # windows
            val = '$HOME\\scimma-security.cfg'
            os.system("SETX {0} {1} /M".format(var, val))
            logging.info('$' + var + ' written as system variable with value ' + val)
        return val


def catcher():
    import configparser
    import sys
    from datetime import date, timedelta

    config = configparser.ConfigParser()

    # proven to work both in package and unpacked form
    import os
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "cfg/defaults.cfg"
    abs_file_path = os.path.join(script_dir, rel_path)
    cfg_sources = [abs_file_path, # built-in config for fallback
                   os.path.expanduser(env_control())  # env value
                  ]
    config.read(cfg_sources)

    loglevel = config.get("DEFAULT", "loglevel", fallback="INFO")
    profile = config.get("DEFAULT", "profile", fallback="scimma-uiuc-aws-admin")


    """Create command line arguments"""
    parent_parser = argparse.ArgumentParser(add_help=False, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parent_parser.add_argument('--loglevel', '-l', help="Level for reporting e.g. DEBUG, INFO, WARN (default: %(default)s)", default=loglevel)
    parent_parser.add_argument('--profile', '-p', default=profile, help='~/.aws/config profile to use (default: %(default)s)')

    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    # request parser augmentation from vault
    from security_scripts.information import vault
    subparsers = vault.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from tag report
    from security_scripts.information import tag_report
    subparsers = tag_report.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from s3 report
    from security_scripts.information import s3_report
    subparsers = s3_report.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from find report
    from security_scripts.information import find_by_content
    subparsers = find_by_content.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from audit
    from security_scripts.controls import audit
    subparsers = audit.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from button actuators
    from security_scripts.controls import buttons
    subparsers = buttons.parser_builder(parent_parser, subparsers, config, True)

    # request parser augmentation from button actuators
    from security_scripts.controls import tests
    subparsers = tests.parser_builder(parent_parser, subparsers, config, True)


    # parse args or handle help
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser_help(parser)
        sys.exit()

    if not args.func or not args:  # there are no subfunctions
        parser_help(parser)
        exit(1)
    logging.basicConfig(level=args.loglevel)


    args.func(args)

if __name__ == "__main__":
    catcher()