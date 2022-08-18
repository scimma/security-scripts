Cloudwatch
==========

Goal
----
Retain logs of access to actions taken on the Scimma AWS account for subsequet
ananlysis including forensic analysis.  Note taht the Scimma does thsi as well as
UIUC.   SCiMMA cannot read the UIUC event trails.  TistedCI advacated this data set
as essential for information security


Data Lifecycle
--------------

The SCiMMA cloud trail  is setup via the console, and would be discontinued by console.


SCiMMA keeps this information for 90 days.  Software in this directory is used to purge older records.  

