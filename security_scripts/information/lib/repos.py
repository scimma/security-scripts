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
import os

class Acquire(measurements.Dataset):
    """
    Load information ffrom giup about repos.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "repos"
        self.make_data()
        self.clean_data()
        
    def netrc_has_credentials(self):
        """Check .netrc for api.github.com credentials"""
        with open(os.path.expanduser("~/.netrc"), 'r') as read_obj:
            for line in read_obj:
                if 'api.github.com' in line:
                    return True
        return False

    def get_members(self, members, level):
        """Generate a string of users with matching privilege level or error message

        :param members: json object containing all repo users
        :param level: single out users with this access level
        :return: string
        """
        if isinstance(members, dict) and 'message' in members.keys():
            return members['message']
        else:
            chosen = ''
            for member in members:
                if member['permissions'][level]:
                    chosen += member['login'] + ', '
            return chosen[:-2]


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

        if self.netrc_has_credentials():
            shlog.normal('using api.github.com login+token from ~/.netrc')
        else:
            shlog.normal('api.github.com credentials not found in ~/.netrc')
            exit(0)

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "CREATE TABLE repos (asset text, description text, url text, who text, can_pull text, can_push text, admins text)"
        shlog.verbose(sql)
        self.q.q(sql)

        #n.b. beta interface when this was coded
        cmd = 'curl -n -H "Accept: application/vnd.github.inertia-preview+json" ' \
              '   https://api.github.com/orgs/scimma/repos'
        import subprocess
        #n.b check will  throw an execption if curl exits with non 0
        #rik is that we get valid output, lokin of like a "404" page.
        repos = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
        repos = json.loads(repos.stdout)
        for repo in repos:
            if repo['private']:
                priv = 'Pri:'
            else:
                priv = 'Pub:'
            asset                         = priv + repo['full_name']
            description                   = repo['description']
            where                         = repo['url'] #url
            who                           = repo['owner']['login']  # is really the account.
            collaborators_url = repo['collaborators_url'].split('{')[0]

            # get user list
            cmd = 'curl -n ' + collaborators_url
            result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
            result = json.loads(result.stdout)
            try:
                # attempt to sort the users
                members                   = {'can_pull':self.get_members(result,'pull'),
                                             'can_push': self.get_members(result, 'push'),
                                             'admins'  :self.get_members(result,'admin')
                                            }
            except subprocess.CalledProcessError:
                # repo is unreadable
                cmd = 'curl -n ' + collaborators_url + ' | jq ".message"'
                result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
                result = json.loads(result.stdout)
                admins                        = result
            sql = "INSERT INTO repos VALUES (?, ?, ?, ?, ?, ?, ?)"
            self.q.executemany(sql, [(asset, description, where, who, members['can_pull'],
                                     members['can_push'], members['admins'])])
        
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

         

    def inf_gitrepo_asset_format(self):
        """
        Report in format for asset catalog. 
        """
        shlog.normal("Reporting in asset foramant")

        sql = '''
              SELECT 'R:'||asset, 'R:'||description, "C" type, 'R:'||url "where", 'R:'||who,
              'R:'||can_pull, 'R:'||can_push, 'R:'||admins  from repos
               '''
        self.df = self.q.q_to_df(sql)


        

