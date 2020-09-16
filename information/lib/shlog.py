#!/usr/bin/env python3
"""
This module implments a subset of logging I use for interactive commands.

by default,  not suppressed are NORMAL, WARN and ERROR, meaning:
    NONE: Produce no output
    NORMAL is comfort messages for the user.
    WARNING is for messages where someting not normal has occurred, but the program continues
    ERROR is for something that is "contract violating" and the program likely needs to termainate

all messages, including the trio NORMAL, WARNING and ERROR are suppressed by setting 
the logging level to "NONE" It is not suported that the trio of NORMAL, WARNING and 
ERROR  are  suppressed individually.

Conceptually orthognal to  the triple of NORMAL, WARN and ERROR is verbosity. 
This modules provides for  three levels of verbosity. the Verbosity levels
help a user understand the program. DEBUG may produce an overwhelming amount
of output, perahpsmroe useful for a bug report. 
    VERBOSE
    VVERBOSE 
    DEBUG.

Progess dots:

Certain application benefit from progress dots.  These are dots (or other symbols) printed to standard 
error wihtoug newlines that denote progress in a long computataion. shlog.dot() and shlog.newline 
are not implemented using the underlying python logging mechansim  They are implemented using writes to stdout. 

"""
import logging
#
# redefine log level text and sugar functions apropos for shell commands, not servers.
# The underlying scheme is that higher the number the more silent the cose will be.
#

NONE=55
NORMAL=logging.FATAL   
DOTS=logging.FATAL-1       # logging.FATAL is 50 at time of writing  Logging.CRITICAL IS 50
WARNING=logging.WARNING     # logging.ERROR is 40  "               "  
ERROR=logging.ERROR     # logging.ERROR is 40  "               "  
VERBOSE=logging.WARNING  # logging.WARNING is 30 "              "
VVERBOSE=logging.INFO    # logging.INFO is 20  "               "
DEBUG=logging.DEBUG      # logging.DEBUG is 10  "             "


LEVELDICT = {"NONE": NONE,
             "NORMAL": NORMAL,
             "DOTS" : DOTS,
             "WARN": WARNING,
             "ERROR" : ERROR,
             "VERBOSE": VERBOSE ,
             "VVERBOSE": VVERBOSE,
             "DEBUG": DEBUG}
for (levelname, levelno) in LEVELDICT.items():
    logging.addLevelName(levelno, levelname)

# re-using the standard logging gives all the sugar features of the logging modues
# so create the "shlog.normal" function to be an alias of logging.normal, etc.
normal = logging.fatal
verbose = logging.warning
vverbose = logging.info
debug = logging.debug
exception = logging.exception
def warn(msg, *args, **kwargs):
    logging.log(LEVELDICT["WARN"], msg, *args, **kwargs)
def error(msg, *args, **kwargs):
    logging.log(LEVELDICT["ERROR"], msg, *args, **kwargs)

def dot(symbol="."):
    #log progress dots, by default dots are a period (.)
    import sys
    loglevel = logging.root.getEffectiveLevel()
    if loglevel > DOTS : return 
    print(symbol, end="", file=sys.stderr)
    
def newline():
    #just a newline, useful if last dot is known and dots are printed
    import sys
    loglevel = logging.root.getEffectiveLevel()
    if loglevel > DOTS : return 
    print("",file=sys.stderr)

def basicConfig(**kwargs):
    # Call underlying loggger
    logging.basicConfig(**kwargs)
    return

helptext = "NONE, NORMAL, NDOTS, VERBOSE, VVERBOSE, DEBUG"

if __name__ == "__main__":

    import argparse
    
    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('loglevel',
                             help=helptext,
                             default="NORMAL")
     
    args = main_parser.parse_args()

    basicConfig(level=LEVELDICT[args.loglevel])

    #generate an outout for each message
    normal("normal message")
    warn("WARN")
    error("ERROR")
    for r in range (1,20): dot()
    newline()
    verbose("verbose message")
    vverbose("verboser message")
    debug("debug message")
 
