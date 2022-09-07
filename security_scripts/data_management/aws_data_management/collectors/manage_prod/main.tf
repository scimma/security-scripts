terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/collectors/prod"
    region = "us-west-2"
  }
}




module "postgres_logs" {
  source = "../postgres_logs"

table_name  = "OpsLogs_prod"
  dynamodb_put_item_policy   = "dynamodb-put-item-policy-prod"

  lambda_basicexecutionrole  =  "lambda-basicexecutionrole-prod"
  postgres_logging_lambda_name = "postgres-logging-lambda-prod"

  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/security-scripts",
                 "lifetime":"forever",
                 "Service":"opsLogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Production",
                 "Name":"Save operations logs"


                 }
}


module "flow_logs" {
  source = "../flow_logs"

  table_name  = "OpsLogs_prod"
  dynamodb_put_item_policy = "dynamodb-put-item-policy-prod"
  lambda_basicexecutionrole  =  "lambda-basicexecutionrole-flow-prod"
  flow_logging_lambda_name = "flow-logging-lambda-prod"

  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/securit-scripts",
                 "lifetime":"forever",
                 "Service":"opsLogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Production",
                 "Name":"Save flow logs"

                 }
}
