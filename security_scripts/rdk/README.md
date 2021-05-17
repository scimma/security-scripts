# Development Area for RDK-based AWS CI controls

## Explain like I'm five.

AWS has a feature called *config*.  Once enabled, *config* montiors
many AWS-level resources (called Confguration Items, or CI's) *Config*
can report newly created and modified Configuration Items to any
number of lambda functions. Such a lambda function can
check newly created resources for compiles with rules.

For starters, *config* can check that configuration items are
consisteent with pre-canned rule sets like the CIS Baseline controls.
All of the rule evaluations an be displayes in the AWS console,
uploaded as files, accessed though the AWS CLI, routes to SLACK, etc.

We can `also write lambda functions to check that AWS CI's comply with
custom rules that SCiMMA has.  AWS calles these custom rules. AWS
supplies some middleware, *rdk*, to support coding these rules,
testing the rules and deploying rules, etc. In the framework provided
by *rdk*, Each rule is a subdiectory (containing a parameters.json
file) of this (rdk) directory.

*Rdk* is only a middleware with a lot of options. The following
scripts that codify some of our conventions for coding and managing
deployments of rules. The scripts are to be run from the rdk
directory.  The scrupts will evolve as we learn. The help from these
scrips will provide more details.

```
./rdk_create.py #creates a rule directory according to our conventions.
```

```
./rdk_manage.py #deploys/undeploys the checking lambda functions, including deployments to multiple availablity zones.
```


