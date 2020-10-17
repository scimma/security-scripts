"""
Common Code not tied to any specific compliance tests
or to AWS.

"""
import pandas as pd
from security_scripts.information.lib import shlog
import sqlite3
import regex as re

class Q:
    "conveience class for common query functionality"
    def __init__(self, dbfile, flush):
        """
        Open a database and maintain a connection to it

        Also, for now assume the DB is a cachen and needs
        to be deleted if stale. Stale == an hour.
        """
        self.dbfile = dbfile
        self.flush = flush
        self._did_purge_cache() # delete stale file.
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()

    def _did_purge_cache(self):
        """
        Determine if database file is too old to use.
        return True if db file purged (or is memory only instance)e
        """
        from security_scripts.information.lib import shlog
        import time
        import os
        import stat
        timeout = 60*60*4
        pathname = self.dbfile

        # if memory DB or file not fond, its "as if" the cache needed to be purgess.
        if pathname == ":memory:" : return True
        if not os.path.isfile(pathname): return True
        dbfile_age =  time.time() - os.stat(pathname)[stat.ST_MTIME]
        if dbfile_age > timeout or self.flush:
            shlog.normal("removing stale database cache {}".format(pathname))
            os.remove(pathname)
            return True
        else:
            shlog.normal("using database cache {}".format(pathname))
            return False

    def executemany(self, sql, list):
        result = self.cur.executemany(sql, list)
        self.conn.commit()
        return result
    
    def q(self, sql):
        """Query and return sqlite result"""
        try:
            result = self.cur.execute(sql)
            self.conn.commit()
            return result
        except sqlite3.OperationalError as oe:
            # error handling
            # already exists table failure
            if re.match('table.*already exists', str(oe)) is not None:
                shlog.normal('sqlite error: ' + str(oe)) #TODO: remove
                return None
            # all other errors need to be raised
            raise oe


    def q_to_df(self, sql):
        """Query and return dataframe"""
        result = self.q(sql)
        headings = [h[0] for h in self.cur.description]
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=headings)
        return df

    def q_to_table(self, sql):
        """Query and return tabulate table"""
        import tabulate
        result = self.q(sql)
        headings = [h[0] for h in self.cur.description]
        rows = result.fetchall()
        table = tabulate.tabulate(rows, headers=headings)
        return table

    def df_to_db(self, table, df) -> None:
        """Insert dataframe into table

        :param table: target table int he connected database
        :param column_tuple: tuple containing
        :return:
        """
        question_marks = len(list(df))
        for line in df.values.tolist():
            value_list = tuple(line)
            sql = "INSERT INTO " + table + " VALUES (" + str('?, '*question_marks)[:-2]  + ")"
            self.executemany(sql, [value_list])


import datetime
import json
class DateTimeEncoder(json.JSONEncoder):
    """
    convert json with a date or datetime object to ISO format string

    use when going from JSON in native "dictionalry form" to
    a string.
    Example: use with the cls keyword in json.dumps.
    """
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def find_string(obj, valuematch, c):
    """
    Return a list of key, value pairs where value matches valuematch
   
   Valuematch can be specifies as a glob style "wildcard"
    """
    import copy
    arr = []
    context = []


def flatten_tags(tag_data):
    '''
    Flatten the way AWS encodes tags to a single dict for editing JSON

    AWs encodes Tags a a list of dicts
    e.g [{"Key":"OwnerEmail","Value":"swnelson@uw.edu"},{"Key":"Criticality","Value":"Development"}]
    this format foes not play well with query tools.
    return a new dicitionary of the formm  {"OwnerEmail":"swnelson@uw.edu", "Criticality":"Development"}
    '''
    retdict = {}
    import pdb; pdb.set_trace
    for dict in tag_data:
        key   = dict["Key"]
        value = dict["Value"]
        retdict[key]= value
    return retdict

def tiny_hash(thing):
    """
    Provide few digit hash from a string

    The idea is to provide a key identifying a thing in a class
    by hashing somethign that is associated, acquireable and semi-stable 
    """
    import zlib
    thing = "{}".format(thing)
    thing = zlib.adler32(thing.encode('utf_8'))
    thing = hex(thing)[-4:]
    return thing
