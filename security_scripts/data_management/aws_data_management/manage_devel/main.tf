terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/devel"
    region = "us-west-2"
  }
}


module "postgress_logs" {
  source = "../postgres_logs"

  table_name  = "PostgresLogs_devel"

  lambda_basicexecutionrole  =  "lambda-basicexecutionrole-devel"
  postgres_logging_lambda_name = "postgres-logging-lambda-devel"
  dynamodb_put_item_policy   = "dynamodb-put-item-policy-devel"
  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/securit-scripts",
                 "lifetime":"forever",
                 "Service":"postgreslogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Development",
                 "Name":"Save postgres logs"


                 }
}