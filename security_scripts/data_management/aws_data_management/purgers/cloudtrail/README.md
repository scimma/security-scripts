Cloudwatch
==========

Goal
----
Retain logs of evevnts tied  actions taken on the Scimma AWS account for subsequent
ananlysis including forensic analysis.  remove logs help longer that the three
mont retention policyTrustedCI


Data Lifecycle
--------------

The SCiMMA cloud trail is setup via the console, and would be discontinued by console.
SCiMMA keeps this information for 90 days.  Software in this directory is used
to purge older records.  


Analysis
--------
Basic Analysis is via the AWS cludtrail console


Notes
-----

SInce this just purges data, and does not make new data, there is no support
for having a seperats "dev" instance