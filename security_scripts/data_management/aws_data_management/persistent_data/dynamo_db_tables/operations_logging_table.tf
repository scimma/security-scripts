//
// make dynamodb related ressources for holdimng postgres logs.
//    aws_dynamodb_table.postgreslogs-dynamo-db-table A dynamBD table
//    aws_iam_policy.postgreslogs-put-item-policy
//    table name will vary  between devel and production.
//    (do not want test data polluting production data)


// uuid as hash kkey prevents any ecord frm begn a duplicate and over  written
resource "aws_dynamodb_table" "operations-dynamo-db-table" {
  name           = var.table_name
  hash_key       = "uuid"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "uuid"
    type = "S"
  }

  attribute {
    name = "activity"
    type = "S"
  }

  attribute {
   name = "utc_date"
   type = "S"
  }


global_secondary_index {
    name               = "activityIndex"
    hash_key           = "activity"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "KEYS_ONLY"
  }

global_secondary_index {
    name               = "utc_date_index"
    hash_key           = "utc_date"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "KEYS_ONLY"
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
  description = "This policy allows a  lamba function to put loga in dynamo db."

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
        "Resource" = aws_dynamodb_table.operations-dynamo-db-table.arn
      }
    ]
  })
  tags = var.standard_tags
}
