terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/collectors/prod"
    region = "us-west-2"
  }
}

module "postgres_logs" {
  source = "../postgres_logs"

  table_name  = "PostgresLogs_prod"
  lambda_basicexecutionrole  =  "lambda-basicexecutionrole-prod"
  postgres_logging_lambda_name = "postgres-logging-lambda-prod"
  dynamodb_put_item_policy   = "dynamodb-put-item-policy-prod"
  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/securit-scripts",
                 "lifetime":"forever",
                 "Service":"postgreslogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Production",
                 "Name":"Save postgres logs"


                 }
}
