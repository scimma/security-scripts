"""
Data Acquisition and Tests/Information for Scimma AWS github repos.

This module has code to collect data github beta API
"""

import pandas as pd
import sqlite3
import measurements
import shlog
import json
import datetime
import vanilla_utils

class Acquire(measurements.Dataset):
    """
    Load information from github about repos.

    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "repos"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        MAKE DATA FOR GIT REPOS.
        """
        if self.does_table_exist():
            shlog.normal("repos  already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = "CREATE TABLE repos (name TEXT, description TEXT, url TEXT, who TEXT, hash TEXT, record JSON)"
        shlog.verbose(sql)
        self.q.q(sql)

        #n.b. beta interface when this was coded
        credentials = self.args.gitcreds
        if credentials:
            credentials = " -u " + credentials
        else:
            shlog.verbose("github audit will only return information available to anonymous user")
            
        cmd = 'curl  -H "Accept: application/vnd.github.inertia-preview+json"   https://api.github.com/orgs/scimma/repos'
        cmd = cmd +  credentials
        
        import subprocess
        #n.b check will  throw an execption if curl exits with non 0
        #rik is that we get valid output, lokin of like a "404" page.
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
            sql = "INSERT INTO repos VALUES (?, ?, ?, ?, ?, ?)"
            self.q.executemany(sql, [(name, description, where, who, hash, record)])

        

class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)

    def make_asset_data(self):
        """
        Make asset data for repos 
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
        r =self.q.q(sql)
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
            "show the returned json"
            sql = "select record from repos"
            return sql
        



    

        

