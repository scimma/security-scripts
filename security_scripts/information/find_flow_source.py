#!/usr/bin/env python
"""
Render an AWS flow long into a more readable format.

Optons available via <command> --help
"""

import tabulate
import time 
import glob
import os

class FlowRecord:
    def __init__(self, args, record):
        self.verssion       = record[0 ]
        self.account_id     = record[1 ]
        self.interface_id   = record[2 ]
        self.srcaddr        = record[3 ]
        self.destaddr       = record[4 ]
        self.srcport        = record[5 ]
        self.dstport        = record[6 ]
        self.protocol       = record[7 ]
        self.packets        = record[8 ]
        self.bytes          = record[9 ]
        self.start          = record[10]
        self.end            = record[11]
        self.action         = record[12]
        self.log_status     = record[13]

    def flow_id(self):
        return self.srcaddr+","+self.destaddr+","+self.srcport+","+self.dstport+","+self.protocol
    

def select_files (args):
    glob_spec = os.path.join("/Users/ekimtco2/.flow_vault/","58519351174*flowlog*.log*")
    filenames =  [name for name in glob.glob(glob_spec)]
    filenames.sort() #does not yeild a set of time ordered logs.
    #i = 0
    #for name in filenames :
    #    print (i, name)
    #    i += 1
    return filenames

def render_dates(args, data):
    """replace unix number time with formatted time."""
    for d in data:
        d[10] = time.ctime(int(d[10]))
        d[11] = time.ctime(int(d[11]))
    return data

def render_protocols(args, data):
    """ replace prootocol number with protocoal name, for common protocols"""
    for d in data:
        if d[7] == '1'  : d[7] = 'icmp'
        if d[7] == '6'  : d[7] = 'tcp'
        if d[7] == '17' : d[7] = 'udp'
    return data

def render_services(args, data):
    """ replace service number with service name, for common services"""
    for d in data:
        for col in [5, 6]:
            if d[col] == '22'   : d[col] = 'ssh'
            if d[col] == '23'   : d[col] = 'telnet'
            if d[col] == '53'   : d[col] = 'domain'
            if d[col] == '80'   : d[col] = 'http'
            if d[col] == '88'   : d[col] = 'kreberos'
            if d[col] == '123'  : d[col] = 'ntp'
            if d[col] == '161'  : d[col] = 'snmp'
            if d[col] == '443'  : d[col] = 'https'
            if d[col] == '563'  : d[col] = 'nntps'
            if d[col] == '636'  : d[col] = 'ldaps'
            if d[col] == '992'  : d[col] = 'telnets'

    return data

def identity(args, flow):
    """
    Return an identity of a flow

    Identity is source, dest sourceport destport protocol  
    """
    pass
    
def detect_span(args, data):
    pass
    
def main(args):
    all_data = []
    for filename  in select_files(args):
        file = open (filename, "r")
        data = file.read() ; file.close()
        data = data.split('\n')
    
        #clean
        #strip off possible blank lines at the end
        while not data[-1] : data.pop(-1)

        #break off into columns and grab header
        data = [d.split(" ") for d in data]
        headers = data.pop(0)

        all_data = all_data + data

    #sort data into time ordered by begin time 
    all_data = sorted(all_data, key=lambda all_data : all_data[10])

    #transform to more readable, if indicated
    if args.render_dates    : data = render_dates(args, all_data)
    if args.render_protocols: data = render_protocols(args, all_data)
    if args.render_services : data = render_services(args, all_data)

    #display
    print (tabulate.tabulate(all_data, headers=headers))
    print ('**, common protocols icmp:1, tcp:6, udp:17')
 
if __name__ == "__main__":

   import os
   import sys
   import time
   import argparse 
   import sqlite3




if __name__ == "__main__":
   """Create command line arguments"""
   parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
   parser.add_argument('--debug','-d',help='print debug info', default=False, action='store_true')
   parser.add_argument('--render_dates','-r',help='render timestamps as localtime', default=False, action='store_true')
   parser.add_argument('--render_protocols','-p',help='render protocol as text', default=False, action='store_true')
   parser.add_argument('--render_services','-s',help='render protocol as text', default=False, action='store_true')
   args = parser.parse_args()
   args.dir = os.path.expandvars('$HOME/Downloads')

   args.filename= os.path.join(args.dir,'585193511743_vpcflowlogs_us-east-1_fl-0421d5b7f8e207da1_20210318T1825Z_630bd7db.log')
   main(args)

