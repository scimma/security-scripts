"""
Provide base classes for acquisition of data and for  measurement/analysis.

The Database class loads information into a sqlite relational DB.
The Measurement class uses the relational db.
The two classes do not otherwise communicate.
"""
from security_scripts.information.lib import shlog
import pandas as pd
import fnmatch
import sys
import boto3
from security_scripts.information.lib import vanilla_utils
import json
import os
from security_scripts.information.lib import aws_utils

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
        #
        # There is no gocd to deal with flattendin the "arrays fo dicionawr with basincally the
        # same keys which are also awkwarb. (tags as arrays of key, falue dictionarie are
        # an example.)
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
        # dir enforcement
        self.args.report_path = os.getcwd() + "/report_files"
        if not os.path.exists(self.args.report_path):
            os.makedirs(self.args.report_path)

        if self.listonly:
            self._print_tests("tst_")
            self._print_tests("inf_")
            self._print_tests("make_")
            self._print_tests("json_")
        else:
            self._call_analysis_methods("tst_",self._write_relational_files)
            self._call_analysis_methods("inf_",self._write_relational_files)
            self._call_analysis_methods("make_",self._null)
            self._call_analysis_methods("json_",self._write_json_file)

    def _call_analysis_methods(self,prefix, report_func):
        """
        Call all methods begining with indicated prefix.
        
        This code uses the python metaclass system
        to find all methods beginning with the indiccated
        prefix and  invoke them.  These methods must have
        no arguments (other than self)

        After testing the report function supplied by the caller
        is invoked.
        """
        

        for name, func in self._list_tests(prefix):
            shlog.normal("starting analysis: %s" % (name))
            #result = func()
            report_func(func)


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

    #
    #  Here are routines that render the output
    #
    def _null(self, func) : pass


    def _print_tests(self, result, prefix):
        """
        Print a list of available tests with the indicated prefix

        Print to stdout.
        """
        for test, _ in self._list_tests(prefix):
            print(test)
        

    def _is_violation_detected(self):
        """Indicate that a test has not suceeded """
        if self.df.size == 0 :
            return False
        return True

    
    def _write_json_file (self, func):
        """
        write a json file from a query containing
        one columm. OUtput file is useabel
        by utileies such as jq.
        """
        name = func.__name__
        filename =  name + ".json"
        filepath = os.path.join(self.args.report_path, filename)
        shlog.normal ("preparing {}".format(filepath))
        sql = func()
        shlog.verbose("sql is: {}".format(sql))

        jsons = self.q.q(sql).fetchall()
        jsons = [j[0] for j in jsons]
        jsons = ",\n".join(jsons)
        jsons = "[" + jsons + "]"
        jsons = jsons.encode(encoding='UTF-8')
        # now  write it out.
        f = open(filepath,'wb')
        f.write(jsons)
        f.close()
        return

    def append_df_to_excel(self, filepath, df, sheet_name):
        """Append a DataFrame [df] to existing Excel file [filepath] into [sheet_name] Sheet.
        If [filepath] doesn't exist, then this function will create it.

        filepath: File path or existing ExcelWriter (Example: '/path/to/file.xlsx')
        df: dataframe to save to workbook
        sheet_name: Name of sheet which will contain DataFrame.
        startrow: upper left cell row to dump data frame.
                   Per default (startrow=None) calculate the last row
                   in the existing DF and write to the next row...
        truncate_sheet: truncate (remove and recreate) [sheet_name]
                         before writing DataFrame to Excel file
        to_excel_kwargs: arguments which will be passed to `DataFrame.to_excel()`

        original https://stackoverflow.com/a/47740262/10086137
        """
        from openpyxl import load_workbook
        writer = pd.ExcelWriter(filepath, engine='openpyxl')

        # Python 2.x: define [FileNotFoundError] exception if it doesn't exist
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError

        try:
            # try to open an existing workbook
            writer.book = load_workbook(filepath)
            # nuke sheet
            if sheet_name in writer.book.sheetnames:
                # index of [sheet_name] sheet
                idx = writer.book.sheetnames.index(sheet_name)
                # remove [sheet_name]
                writer.book.remove(writer.book.worksheets[idx])
                # create an empty sheet [sheet_name] using old index
                writer.book.create_sheet(sheet_name, idx)

            # copy existing sheets
            writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
        except FileNotFoundError:
            # file does not exist yet, we will create it
            shlog.normal("creating excel file  {}".format(filepath))

        # write out the new sheet and save
        df.to_excel(writer, sheet_name, index=False)
        writer.save()

    def _write_relational_files(self, func):
        """
        Write a relational report out in tablular and csv formnt
        """
        name = func.__name__
        txt_filename =  name + ".txt"
        filepath = os.path.join(self.args.report_path, txt_filename)
        shlog.normal ("preparing {}".format(filepath))
        sql = func()
        shlog.verbose("sql is: {}".format(sql))
        df = self.q.q_to_df(sql)
        # wrapped table )qicj look for human
        table = wrapped_ascii_table(self.args, df).encode(encoding='UTF-8')
        f = open(filepath, "wb")
        f.write(table)
        f.close()
        # csv
        csv_filename =  name + ".csv"
        filepath = os.path.join(self.args.report_path, csv_filename)
        shlog.normal ("preparing {}".format(filepath))
        df.to_csv(filepath, index=False)
        # add to excel workbook
        # Thsi code is not working, it's be nice to have all this in workbook.
        # needs to be cloasds
        xlxs_filename =  "all.xlsx"
        filepath = os.path.join(self.args.report_path, xlxs_filename)
        # import pdb; pdb.set_trace()
        shlog.normal("adding sheet {} to {}".format(name, filepath))
        self.append_df_to_excel(filepath, df, name)

    
             
        
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
