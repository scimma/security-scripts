
# Concept of Operations

## Steady State Concept
Prerequisites: The postgres databases are configured to send their logs to cloudwatch. Ideally,
the postgres databases have been configured with a non-default parameter group, so we can tweak
the verbosity of the logs.

A Lambda function read the cloudwatch logs, and re-formats the invormatkion and add a special field instucting dynamo DB
to purge the records after three month. The code then forwards the entries to a dynamo DB table. Dynamod  DB automatically removes
thes records after three months.  Data from all postgres instance is forwarded to a single table.
Database  entries identify the originating postgres data base.

## starting stopping
The terraform is factored into persistent_data and collectors.  This allows collectors to be destroyed without
destroying (especially) the production database.

To start a development session from scratch
```
cd persistent_data/manage_devel ; terraform apply
cd collectors/manage_devel/main.tf ; terrafrom apply
```

To stop data collection, destroy the  collectors


```
#to (mostly) stop the development instance
cd collectors/manage_devel/main.tf ; terrafrom destroy
cd persistent_data/mananage_devel/main.tf ;  terrafrom destroy 

#to stop the producion system
cd collectors/manage_dprod/main.tf ; terrafrom destroy
Dynammo DB will delete recod when they are three months old.

```

## Notes:

Postgres Logging  uses cloudwatch log groups .  The default length of
retention for cloudwatch is "infinite"  and should be changed.
Two weeks retention seems reasonable and is the reccomended default for
this application.

The lanbda funcion itself  generates a cloudwatch log for its suport/
debug.  One log is geneerates bu the development instance, another by the
producton instnace.  These are nto currenlty created by terraform, its
important so manually set the retention period of these cloudatch logs.






# Files/directories and their function:

```
persistent_data/manage_devel:main.tf     #makes/destroys the devlopement dynamo DBN.
persistent_data/manage_prod:main.tf      #makes/destroty the producitn dynamo DB  databases 

collectors/manage_devel/main.tf   #starts the collectors, does not make or destroy the corresponding dynamo DB table
collectors/manage_prod/main.tf    #starts the collectors, does not make or destroy the corresponding dynamo DB table

collectors/postgres_logs:*  code for the lambda that collects postgres logs and forwards them to dynamo DB.
persistent_data/dynamo_db_tables:/* code to the dynaamo DB table that hold logs in a queryable form    
```

