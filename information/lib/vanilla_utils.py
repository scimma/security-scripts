"""
Common Code not tied to any specific compliance tests
or to AWS.

"""
import pandas as pd
import sqlite3

class Q:
    "conveience class for common query functionality"
    def __init__(self, dbfile):
        """
        Open a database and maintain a connection to it

        Also, for now assume the DB is a cachen and needs
        to be deleted if stale. Stale == an hour.
        """
        self.dbfile = dbfile
        self._did_purge_cache() # delete stale file.
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()

    def _did_purge_cache(self):
        """
        Determine if database file is too old to use.
        return True if db file purged (or is memory only instance)e
        """
        import shlog
        import time
        import os
        import stat
        timeout = 60*60
        pathname = self.dbfile

        # if memaory DB or file not fond, its "as if" the cache needed to be purgess.
        if pathname == ":memory:" : return True
        if not os.path.isfile(pathname): return True
        dbfile_age =  time.time() - os.stat(pathname)[stat.ST_MTIME]
        if dbfile_age > timeout:
            shlog.normal("removing stale database cache {}".format(pathname))
            os.remove(pathname)
            return True
        else:
            shlog.normal("using database cache {}".format(pathname))
            return False

                                                    
    def q(self, sql):
        """Query and return sqlite result"""
        result = self.cur.execute(sql)
        self.conn.commit()
        return result

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

