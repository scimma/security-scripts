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
    Load information from github about repos.

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
        sql = "CREATE TABLE repos (name TEXT, description TEXT, url TEXT, who TEXT, " \
              "can_pull text, can_push text, admins text, hash TEXT, record JSON)"
        shlog.verbose(sql)
        self.q.q(sql)

        #n.b. beta interface when this was coded
        cmd = 'curl -n -H "Accept: application/vnd.github.inertia-preview+json" ' \
              '   https://api.github.com/orgs/scimma/repos'
        import subprocess
        #n.b check will  throw an execption if curl exits with non 0
        #rik is that we get valid output, lokin of like a "404" page.
        shlog.verbose(cmd)
        result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
        stdout = result.stdout
        stderr = result.stderr
        if len(result.stdout) < 200:
            shlog.verbose("github curl error: stdout:{} stderr:{}".format(stdout, stderr))
            exit(1)
        result = json.loads(result.stdout)
        for repo in result:
            # import pdb; pdb.set_trace()
            name                          = repo['full_name']
            description                   = "{}(Private={})".format(repo['description'],repo['private'])
            where                         = repo['url'] #url
            who                           = repo['owner']['login']  # is really the account.
            hash                          = vanilla_utils.tiny_hash(name)
            record                        = json.dumps(result)

            # get user list
            collaborators_url = repo['collaborators_url'].split('{')[0]
            cmd = 'curl -n ' + collaborators_url
            result = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
            result = json.loads(result.stdout)
            try:
                # attempt to sort the users
                members = {'can_pull': self.get_members(result, 'pull'),
                           'can_push': self.get_members(result, 'push'),
                           'admins': self.get_members(result, 'admin')
                           }
            except subprocess.CalledProcessError:
                # repo is unreadable
                cmd = 'curl -n ' + collaborators_url + ' | jq ".message"'
                CPE = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True)
                CPE = json.loads(result.stdout)
                admins                     = result
            sql = "INSERT INTO repos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            self.q.executemany(sql, [(name, description, where, who, members['can_pull'],
                                     members['can_push'], members['admins'], hash, record)])


class Report(measurements.Measurement):
    def __init__(self, args, name, q):
        measurements.Measurement.__init__(self, args, name, q)

    def make_asset_data(self):
        """
        Make  table(s) for interetion into the master asset table.
        """

        sql = '''
         CREATE TABLE asset_data_repos  AS
              SELECT
                     "git_repo_"||hash                                   tag,
                     "R:Contents of: "||name                           asset,
                     "R:Source Materials for "||description      description,
                     "D:Maintains source files for topic"     business_value,
                     "D:None, open to public"                       impact_c,
                     "D:contents corrupted"                         impact_i,
                     "D:users of data disrupted"                    impact_a,
                     "D"                                                type,
                     "R:"||url                                       "where",
                     "R:"||who                                           who  
               FROM  repos
        '''
        shlog.vverbose(sql)
        r = self.q.q(sql)
        sql = '''
            CREATE TABLE asset_data_repo_credentials  AS
              SELECT
                     "git_repo_"||hash                                                        tag,
                     "R:Credentials to administer/read/write Git repo: "||name              asset,
                     "R:Defines who can drop/write/read the repo "||description       description,
                     "D:PRovides access control to repo for staff and community "  business_value,
                     "D:disruption by repo write or rpo admin creds"                     impact_c,
                     "D:Lost? user uses github to replace credential"                    impact_a,
                     "C"                                                                     type,
                     "R: Personal (not SCiMMA controlled github identity "                "where",
                     "R: Staff authorized to administer/read/write repo"                      who
              FROM repos
               '''
        shlog.vverbose(sql)
        r = self.q.q(sql)

    def inf_json(self):
        "show the returned repos json"
        sql = "select record from repos"
        return sql

    def inf_repos(self):
        " repos report"
        sql = "select name, description, url, who, can_pull, can_push, admins, hash from repos"
        return sql




