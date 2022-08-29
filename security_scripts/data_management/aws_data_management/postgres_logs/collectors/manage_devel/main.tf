terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/collectors/devel"
    region = "us-west-2"
  }
}




module "postgres_logs" {
  source = "../postgres_logs"

// teh follwing should really be commedced to the output
// of the dyanamo DB module from persistent storage.
// but I've not learned how to do that yet.
// so senseless duplications for now

  table_name  = "OpsLogs_devel"
  dynamodb_put_item_policy = "dynamodb-put-item-policy-devel"

  lambda_basicexecutionrole  =  "lambda-basicexecutionrole-devel"
  postgres_logging_lambda_name = "postgres-logging-lambda-devel"

  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/securit-scripts",
                 "lifetime":"forever",
                 "Service":"opsLogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Development",
                 "Name":"Save operations logs"


                 }
}