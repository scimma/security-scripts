#!/usr/bin/env python3
"""
lsearch.py -- search the SCiMMA ldap using the ldapsearch tool.

By default, no query specficfied, the LDAP schema is dumped,
otherwise the results of the query is dumped.

Example LDAP queries, including best practice to quote this argument.
 '(voPersonID=SCiMMA1000000)'
 '(cn=*and*)'

LDAP passwords are assumeed to be in $HOME/.ldap/<server-name>
Note that the files can contain only the password, and not even
a newline in the file.

Optons available via <command> --help
"""


COMMAND_TEMPLATE = """ldapsearch \
    -LLL \
    -H ldaps://ldap.cilogon.org \
    -D 'uid=readonly_user,ou=system,o=SCiMMA,o=CO,dc=scimma,dc=org' \
    -x \
    -y %s \
    -b ou=people,o=SCiMMA,o=CO,dc=scimma,dc=org \
    %s
"""

def main(args):
   "Print the result of the commend on stdout"
   
   server =  args.server
   if args.query:
      args.query = "'" +  args.query + "'"
   else:
      args.query = ""

   passfile = pathlib.Path.expanduser(pathlib.Path("~/.ldap", args.server))
   logging.debug ("password file: %s" % passfile)
   cmd = COMMAND_TEMPLATE % (passfile, args.query)
   logging.debug("cmd :%s" % cmd)
   os.system(cmd)
   

if __name__ == "__main__":

   import os
   import sys
   import argparse
   import logging 
   import pathlib


   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--server','-s',default='ldap.cilogon.org',
             help='one of ldap.cilogon.org, ldap-test.cilogon.org')
   parser.add_argument('--debug','-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('query', nargs='?', default=None)     
   args = parser.parse_args()
   if args.debug :
      loglevel = getattr(logging, "DEBUG")
   else:
      loglevel = getattr(logging, "INFO")
   logging.basicConfig(level=loglevel)
   main(args)

