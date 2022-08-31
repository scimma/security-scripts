//
// refer to  dynamodb related ressources for holdimng postgres logs.
//    aws_dynamodb_table.postgreslogs-dynamo-db-table
//    aws_iam_policy.postgreslogs-put-item-policy
//    table name will vary  between devel and production.
//    (do not want test data polluting production data)
data "aws_dynamodb_table" "postgreslogs-dynamo-db-table" {
  name           = var.table_name
}

data "aws_iam_policy" "dynamodb-put-item-policy" {
  name        = var.dynamodb_put_item_policy
}