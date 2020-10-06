"""
Data Acquisition and Tests/Information for filling out the Scimma Asset table
as far as acquireable data allows

The module is a backend to all other acquition and reporting modules.
These modules produce input via databse tables whose names begin with
asset_data.  This module inspects  all database tablee beginning with
asseet_data to see if there are any shared column names with the
assets table it defines iself.   If so, this module populates rows of the
assets table with the data from the precursor table   Any missing columns are
left to the default valus (null). Ths allows for gradual evolution of
the population of the asset table --  Acquistion modules need not supply
all columns -- just what they can detect  or make up reasonable  defaults.

"""

from security_scripts.information.lib import measurements
from security_scripts.information.lib import shlog

class Acquire(measurements.Dataset):
    """
    Make Asset data from Precursor tables 
    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "assets"
        self.asset_columns = ('tag', 'asset', 'description', 'business_value','impact_c',
                              'impact_i','impact_a', 'type', '"where"', 'who')
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        MAKE DATA FOR GIT REPOS.
        """
        if self.does_table_exist():
            shlog.normal("Assets  already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Master Table for other reports to  deposit asset data they 
        # one tag, value pair in each record.
        sql = "CREATE TABLE {} ({} TEXT)".format(self.table_name, " TEXT, ".join(self.asset_columns))
        shlog.vverbose(sql)
        self.q.q(sql)

        # get all the tables.
        sql = """
           SELECT name FROM sqlite_master
           WHERE type IN ('table','view')
           AND name NOT LIKE 'sqlite_%'
           AND name     LIKE 'asset_data%' 
           ORDER BY 1;
        """
        for table in self.q.q(sql).fetchall():
            table = table[0] #one item selects are retuned in a list.
            #
            # Below is a Massive query fond on the web to ger
            # column meta-data out of sqlite I'd like to
            # finds somemething simpler, but don;t want to touch this
            sql = """
               SELECT m.name as tableName,
                  p.name as columnName,
                  p.type as columnType
               FROM sqlite_master m
               left outer join pragma_table_info((m.name)) p
               on m.name <> p.name
             WHERE m.name is '{}'
             AND columnName in {}
             order by tableName, columnName
             """.format(table, self.asset_columns)
            shlog.vverbose(sql)
            #
            # Now get a string with col, cl, cos 
            #
            cols = [col for (_, col, _) in self.q.q(sql)]
            if not cols:
                shlog.verbose ("{} has no matching columns for asset table".format(table))
                continue      
            cols_text = ", ".join(cols)
            
            #
            # and populate the assets table with 
            # fields that match
            #
            sql = """
              INSERT INTO assets ({}) 
             SELECT {} from {}
              """.format(cols_text, cols_text, table)
            shlog.vverbose (sql)
            self.q.q(sql)
        
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

         

    def inf_all_asset_information(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting all asset information")
        
        sql = '''
              SELECT *
               FROM  assets
               ORDER BY tag
               '''
        return sql



    

        

