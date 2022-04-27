terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/persisent_data/prod"
    region = "us-west-2"
  }
}


// Make the dynamo db table used for postgress logging.
//
module "dynamo_db_tables" {
  source = "../dynamo_db_tables"
  table_name = "PostgresLogs_prod"

  dynamodb_put_item_policy_name =  "dynamodb-put-item-policy-prod"
  standard_tags = {
                 "createdBy":"securityAdmin",
                 "repo":"github.com:scimma/security-scripts",
                 "lifetime":"forever",
                 "Service":"postgreslogs",
                 "OwnerEmail":"petravic@illinois.edu",
                 "Criticality":"Production",
                 "Name":"Table to save postgres logs"
                 }
}



///
/// A bad hack for now -- I need to understand the
/// Syntax/Structure for referring to a common definition
//. the module and the these output statements can use 
/// still a newbie at this time
///
output "table_name" {
    value = "PostgresLogs_prod"
   }

output "put_item_policy" {
    value = "dynamodb-put-item-policy-prod"
   }




