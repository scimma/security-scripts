Goal
----
The goal is to collect and retain flow logs recording communication of
the SCiMMA production, development and infrastructure VPCs and retain
these records for operational and information security analysis.


Theory of operation.
--------------------
The records of each of the production, development and infrastrucuture
enclaves are kept in distinct cloudwatch log groups as follows.
Only "active" flowa are kept. 

```
/scimma/network/flows/raw/accept/HopDevel   flows-raw-accept-HopDevel  
/scimma/network/flows/raw/HopInfra          flows-raw-accept-HopInfra
/scimma/network/flows/raw/acccept/HopProd   flows-raw-accept-HopProd

```

The default format provided by AWS is used:

```
${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-stat\
us}
```

The following IAM polices and roles support the ingestion
```
scimma-cloudwatch-flow-ingestion-policy
scimma-cloudwatch-flow-ingestor-role
```
Notes
-----

This should be converted to terraform. the currrent setup  was made by point-and-click.

permissions need to be tightended for the creation of creating the cloudwatch logs. 
arn:aws:logs:us-west-2:585193511743:log-group:aws//scimma/network/flows/*

The Criticality level is always production, as the collection of 
information security data is a production activity, even in the
delvelopment VPC. "devel" might be used for an alernate cloudwatch
implementation,


Access/Analysis
---------------

Analysis is via the cloudwatch console, under "log insights"

