Cloudwatch
==========

Goal
----
Retain logs of evevnts tied  actions taken on the Scimma AWS account for subsequet
ananlysis including forensic analysis.  TrustedCI advacated this data set
as essential for information security


Data Lifecycle
--------------

The SCiMMA cloud trail is setup via the console, and would be discontinued by console.

SCiMMA keeps this information for 90 days.  Software in this directory is used
to purge older records.  


Analysis
--------
Basic Analysis is via the AWS console.