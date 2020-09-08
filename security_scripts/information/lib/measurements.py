"""
Provide base classes for acquisition of data and for  measurement/analysis.

The Database class loads information into a relational DB.
THe Measurement class uses the relational db.
The two classes do not otherwise communicate.
"""
import logging
import pandas as pd

class Dataset:
    """
    Base Class for  acquiring and  preparing a data set of interest for an analysis.
    """
    
    def __init__(self, args, name, q):
        self.args=args
        self.q=q
        self.name=name
        self.table_name = None

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
        logging.debug(sql)
        df = self.q.q_to_df(sql)
        print(wrapped_ascii_table(df))

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

        self._call_analysis_methods("tst_",self._print_test_report)
        self._call_analysis_methods("inf_",self._print_information_report)
        
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
        

        for key in dir(self):
            if key[0:len(prefix)] == prefix:
                #import pdb; pdb.set_trace()
                logging.info("starting analysis: %s" % (key))
                self.current_test = key
                self.__getattribute__(key)()
                report_func() #differnt report format for test/analysis


    def _is_violation_detected(self):
        """Indicate that a test has not suceeded """
        if self.df.size == 0 :
            return False
        return True
    
    def _print_test_report(self):
        """Generate a text report for a single test """
        print()
        print("******* Begin %s ************" % (self.current_test))
        if self._is_violation_detected():
            print("****** Violation Information *****")
            print(wrapped_ascii_table(self.df))
        else:
            print("passed test")
        print("******* End %s ************" % (self.current_test))

    def _print_information_report(self):
        """Generate a information report for a single information analysis """
        print()
        print("******* Begin %s ************" % (self.current_test))
        print(wrapped_ascii_table(self.df))
        print("******* End %s ************" % (self.current_test))



def wrapped_ascii_table(df):
    """
    Return a table with long lines wrapped within a table cell, given a df.

    The table is formed by tabulate 
    """
    import tabulate
    scratch = pd.DataFrame()  # do nt alter caller's data
    for c in list(df.columns):
       #put newlines in the data frame
        scratch[c] = df[c].str.wrap(20)

       #Make a tabulate table, with wrapped data, column headnign and
       #ASCII art to draw cell boindaris.
    table =tabulate.tabulate(scratch, list(scratch.columns),"grid")
    return table   
