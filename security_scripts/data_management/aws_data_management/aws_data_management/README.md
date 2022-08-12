
# Concept of operations

The postgraes databases are configured to send their logs to cloudwatch. Ideally the postgres databases have
been configured with a non-default parameter group, so we can tweak the verbosity of the logs.

Lambda functions read teh cloudwatch logs, an dforward the entries to a dynamo DB table which is set
to hold information for three months, then auto expire.

THE terraform is factroed into persistent_data and collectors.  This allows collectors to be destrory without
destroyng (especially) the production database.

TO start a devleopment session from scratch
> cd persistent_data/manage_devel ; terraform apply
> cd collectors/manage_devel/main.tf ; terrafrom apply




# Files/directories and their function:

> persistent_data/manage_devel:main.tf     #makes/destroys the devlopement dynamo DBN.
> persistent_data/manage_prod:main.tf      #makes/destroty the producitn dynamo DB  databases 


> collectors/flow_logs: #beginng of delveoper for keeping flow logs acress the "borer" fo SCIMMA and the general internte
> collectors/manage_devel/main.tf   #starts the collectos, does not make or desroy the correslonding dynamo DB table
> collectors/manage_prod/main.tf    #starts the collectos, does not make or desroy the correslonding dynamo DB table

> collectors/postgres_logs:*  code for the lambda that collects postgres logs and forwards them to dynamo DB.
> persistent_data/dynamo_db_tables:/* code to teh dybano DB table that hold logs n a queryabvel sofrm    



# A terraform destroy does not completely remove all state from AWS.
There are cloudwatch logs of the python logging messages that are not cleaned up.
These by default are "persist forever? I adjust them from the console.
