"""
Data Acquisition and Tests/Information for Scimma AWS github repos.

This module has code to collect data github beta API
"""

import pandas as pd
import sqlite3
from security_scripts.information.lib import measurements
from security_scripts.information.lib import shlog
import json
import datetime
from security_scripts.information.lib import vanilla_utils

class Acquire(measurements.Dataset):
    """
    Load information ffrom giup about repos.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "repos"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        Make a table called TAGS based on tagging data.
        This collection of data is based on the resourcetaggingapi

        If the tags table exists, then we take it data collection
        would result in duplicate rows. 
        """
        if self.does_table_exist():
            shlog.normal("repos  already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "CREATE TABLE repos (asset text, description text, url text, who text, admins text)"
        shlog.verbose(sql)
        self.q.q(sql)

        temptoken = '' #TODO: a good job of not checking this in
        #n.b. beta interface when this was coded
        cmd = 'curl   -H "Accept: application/vnd.github.inertia-preview+json" ' \
              '-H "Authorization: Token ' + temptoken + '"' \
              '   https://api.github.com/orgs/scimma/repos'
        import subprocess
        #n.b check will  throw an execption if curl exits with non 0
        #rik is that we get valid output, lokin of like a "404" page.
        result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
        result = json.loads(result.stdout)
        for repo in result:
            if repo['private']:
                priv = 'Pri:'
            else:
                priv = 'Pub:'
            asset                         = priv + repo['full_name']
            description                   = repo['description']
            where                         = repo['url'] #url
            who                           = repo['owner']['login']  # is really the account.
            collaborators_url = repo['collaborators_url'].split('{')[0]
            record                        = result

            # get admin list
            cmd = 'curl ' + collaborators_url + ' ' \
                  '-H "Authorization: Token ' + temptoken + '" | ' \
                  'jq "[ .[] | select(.permissions.admin == true) | .login ]"'
            try:
                result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
                result = json.loads(result.stdout)
                admins                        = ', '.join([str(item) for item in result])
            except subprocess.CalledProcessError:
                # oh no, we can't read the repo! let's find out why
                cmd = 'curl ' + collaborators_url + ' ' \
                      '-H "Authorization: Token ' + temptoken + '" | jq ".message"'
                result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
                result = json.loads(result.stdout)
                admins                        = result
            sql = "INSERT INTO repos VALUES (?, ?, ?, ?, ?)"
            self.q.executemany(sql, [(asset, description, where, who, admins)])
        
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

         

    def inf_gitrepo_asset_format(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting in asset foramant")
        
        sql = '''
              SELECT 'R:'||asset, 'R:'||description, "C" type, 'R:'||url "where", 'R:'||who, 'R:'||admins  from repos
               '''
        self.df = self.q.q_to_df(sql)


        

