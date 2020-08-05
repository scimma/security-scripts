"""
Common Code not tied to any specific compliance tests
or to AWS.

"""
import pandas as pd
import sqlite3

class Q:
    "convenince class for common query functionality"
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()

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

