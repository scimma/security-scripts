"""
Provide base classes for acquisition of data and for  measurement/analysis.

The Database class loads information into a sqlite relational DB.
The Measurement class uses the relational db.
The two classes do not otherwise communicate.
"""
import shlog
import pandas as pd
import fnmatch
import sys
import boto3
import aws_utils
import vanilla_utils
import json

class Dataset:
    """
    Base Class for  acquiring and  preparing a data set of interest for an analysis.
    """
    
    def __init__(self, args, name, q):
        self.args=args
        self.q=q
        self.name=name
        self.table_name = None

    def does_table_exist(self):
        """
        Determine if table exist, indicating it has been populated w/ cached data
        """
        import sqlite3 #for exception value
        try:
            sql = "SELECT * FROM {}".format(self.table_name)
            ans = self.q.q(sql)
            return True
        except sqlite3.OperationalError:
            return False
        
    def _json_clean_dumps(self, json_native):
        """ convert native json into text

             Deal with Amazon stuff that is awkward in
             thw tools  set(python, etc)
        """

        # Amazon binarites have datetime types need an encode to turn to text
        # I've not looked  into tiemzones.
        enc = vanilla_utils.DateTimeEncoder  #converter fo datatime types -- not supported
        json_text = json.dumps(json_native, cls=enc)
        return json_text
    
    def _pages_all_regions(self, aws_client_name, aws_function_name):
        """
        An interator that gets the pages for all regions.

        aws_client_name = "resorurcemappingapi"
        functon_name = "get_resources"

        Can be used in for loops producing list of pages on a topic
        """
        self.args.session = boto3.Session(profile_name=self.args.profile)
        region_name_list = aws_utils.decribe_regions_df(self.args)['RegionName']
        for region_name in region_name_list:
            client = self.args.session.client(aws_client_name,region_name=region_name)
            paginator = client.get_paginator(aws_function_name)
            shlog.verbose('about to iterate: {} {}'.format(aws_client_name, aws_function_name))
            page_iterator = paginator.paginate()
            for page in page_iterator:
                yield page

    def make_data(self):
        """ Build base of data needed for the indicated measurement """
        pass

    def clean_data(self):
        """  Remove items that are not relevant"""
        pass

    def print_data(self):
        """
        Print the dataset
        
        This method is provided primariy for debug.
        This method is useful after the make_data and clean steps
        """
        sql = "select * from %s" % (self.table_name)
        shlog.verbose(sql)
        df = self.q.q_to_df(sql)
        print(wrapped_ascii_table(self.args, df))

        
class Measurement:
    """
    Perform a number of tests against the data
    test methods begin with the characters tst_,
    and information methods beginning with inf_
        
    The result of each test is a dataframe
    giving information about the defects found.
    An Empty data frame indicates that no defects were
    found.

    The Result of each informational method is
    a tabular presentation on the screen.
    """
    def __init__(self, args, name, q):
        self.args=args
        self.q=q
        self.name=name
        self.df = None
        self.current_test=None
        self.listonly = args.listonly
        self.args.report_path="./report_files"

        if self.listonly:
            self._print_tests("tst_")
            self._print_tests("inf_")
            self._print_tests("make_")
            self._print_tests("json_")
        else:
            self._call_analysis_methods("tst_",self._print_test_report)
            self._call_analysis_methods("inf_",self._print_relational_report)
            self._call_analysis_methods("make_",self._null)
            self._call_analysis_methods("json_",self._write_json_from_sql)

    def _null(self, result, doc) : pass
    def _call_analysis_methods(self,prefix, report_func):
        """
        Call all methods beginninng with indicated prefix.
        
        This code uses the python metaclass system
        to find all methods beginning with the indiccated
        prefix and  invoke them.  These methods must have
        no arguments (other than self)

        After testing the report function supplied by the caller
        is invoked.
        """
        

        for name, func in self._list_tests(prefix):
            shlog.normal("starting analysis: %s" % (name))
            result = func()
            report_func(result, func.__doc__)


    def _list_tests(self, prefix):
        """
        return list of all tests

        each list element is a parit of  [ascii_name, function-to-call]
        filter according to th eglob in args.only
        """
        list = []
        for key in dir(self):
            if key[0:len(prefix)] == prefix:
                if not fnmatch.fnmatch(key, self.args.only) : continue
                list.append([key, self.__getattribute__(key)])
        return list

    def _print_tests(self, result, prefix):
        """
        print a list of available tests with the indicated prefix
        """
        for test, _ in self._list_tests(prefix):
            print(test)
        

    def _is_violation_detected(self):
        """Indicate that a test has not suceeded """
        if self.df.size == 0 :
            return False
        return True

    def _filepath_from_query(self, sql):
        """
        Compute a pathname from a query

        Derive table name from the table name in the query.
        NOT sure this is robust
        """
        import shlex
        import os
        sql = sql.lower()
        tokens = shlex.split(sql.lower())
        for token, next_token in zip(tokens, tokens[1:]+[""]):
            if token == "from" : table = next_token
        filename = table + ".json"
        filepath = os.path.join(self.args.report_path, filename)
        return filepath


    def _write_json_from_sql (self,sql, doc):
        """
        write a json file from a query containing
        one columm
        """
        import pdb ; pdb.set_trace()
        jsons = self.q.q(sql).fetchall()
        jsons = [j[0] for j in jsons]
        jsons = ",\n".join(jsons)
        jsons = "[" + jsons + "]"
        jsons = jsons.encode(encoding='UTF-8')
        # now  write it out.
        filepath = self._filepath_from_query(sql)
        f = open(filepath,'wb')
        f.write(jsons)
        f.close()
        return
    
    def _print_test_report(self, result, doc):
        """Generate a text report for a single test """
        print("*****{}".format(doc))
        print("******* Begin %s ************" % (self.current_test))
        if self._is_violation_detected():
            print("****** Violation Information *****")
            print(wrapped_ascii_table(self.args, self.df))
        else:
            print("passed test")
        print("******* End %s ************" % (self.current_test))

    def _print_relational_report(self, result, doc):
        """Generate a information report for a single information analysis """
        print("*****{}".format(doc))
        print("******* Begin %s ************" % (self.current_test))
        print(wrapped_ascii_table(self.args,self.df))
        print("******* End %s ************" % (self.current_test))



def wrapped_ascii_table(args, df):
    """
    Return a table with long lines wrapped within a table cell, given a df.

    The table is formed by tabulate 
    """
    import tabulate
    scratch = pd.DataFrame()  # do not alter caller's data
    if args.bare:
        table =tabulate.tabulate(df, list(df.columns))
        return table
    width = int(132/len(df.columns))
    for c in list(df.columns):
       #put newlines in the data frame
        scratch[c] = df[c].str.wrap(width)

       #Make a tabulate table, with wrapped data, column headnign and
       #ASCII art to draw cell boindaris.
    table =tabulate.tabulate(scratch, list(scratch.columns),"grid")
    return table   
