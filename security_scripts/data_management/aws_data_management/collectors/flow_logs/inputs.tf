//
// refer to  dynamodb related ressources for holding flow logs.
//    aws_dynamodb_table.flowlogs-dynamo-db-table
//    aws_iam_policy.flowlogs-put-item-policy
//    table name will vary  between devel and production.
//    (do not want test data polluting production data)
data "aws_dynamodb_table" "flowlogs-dynamo-db-table" {
  name           = var.table_name
}

data "aws_iam_policy" "dynamodb-put-item-policy" {
  name        = var.dynamodb_put_item_policy
}