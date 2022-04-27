//
// make dynamodb related ressources for holdimng postgres logs.
//    aws_dynamodb_table.postgreslogs-dynamo-db-table A dynamBD table
//    aws_iam_policy.postgreslogs-put-item-policy
//    table name will vary  between devel and production.
//    (do not want test data polluting production data)


resource "aws_dynamodb_table" "postgreslogs-dynamo-db-table" {
  name           = var.table_name
  hash_key       = "logStream"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  attribute {
    name = "logStream"
    type = "S"
  }

  ttl {
    attribute_name = "expTime"
    enabled        = true
  }


  tags = var.standard_tags
}

resource "aws_iam_policy" "dynamodb-put-item-policy" {
  name        = var.dynamodb_put_item_policy_name
  path        = "/"
  description = "This policy allows the lamba function to put loga in dynamo db."

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" = "PutItem",
        "Action" = [
          "dynamodb:PutItem",
        ],
        "Effect"   = "Allow",
        "Resource" = aws_dynamodb_table.postgreslogs-dynamo-db-table.arn
      }
    ]
  })
  tags = var.standard_tags
}
