# Development Area for RDK-based AWS CI controls

## Explain like I'm five.
AWS has a feature called *config*.  Once enabled *config* montiors many of our AWS-level resource (or Confguration Item)
*Config* can report newly created and modified Configuration Items  to any number of lambda functions. One thing
such a lambda function can do is check newly created resource  compiles with  rules. Config can check that Configuration
item are consisteent with   pre-canned rule sets like the CIS Baseline controls.

All of the rule evalaution an be displated in the AWS console, uploaded as files, accessed though the AWS CLI, 

We can also write lambda functions to check that AWS CI's comply with custom rules that SCiMMA has.  AWS Supplies some
middleware, **RDK*,  to support coding these rules, testing the rules and deploying etc. IN the framework providedd by
RDK, Each rule is a subdiectory (containing a parameters.json file) of this (rdk) directory.

rdk is only a middleware so we have coded the followin scrips that codify some of our conventions for coding and
managing deplolyme of rules.

```
rdk_create.py creates a rule directory according to our conventions.
```

```
rdk_manage.py deploys and undeploys the checking lambda functions, including deployments to multiple availablity zones.
```


