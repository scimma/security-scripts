
//
//  Setup a lambda function to lof data from one postgres data.
// The data comes to this faclity via cloudwatch.
// The setup of cloudwatch is not done in this faclilty
// logs are processed and (curretly) sent to a databse table
//


// Create a lambda and all of its permssions.
//==============================================
// create a role for this lambda and
// grant the ablity to be a lambda.

resource "aws_iam_role" "postgres-logging-lambda-role" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  tags = var.standard_tags
}


// Make  a policy allowing the lambda function to log itself
resource "aws_iam_policy" "postgres-logging-lambda-policy" {
  name = var.lambda_basicexecutionrole

  policy = jsonencode({
    Version = "2012-10-17"
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*"
      }
    ]
  })
  tags = var.standard_tags
}


// Attach the policy allowing logging the lambda itself to lambda's role 
resource "aws_iam_role_policy_attachment" "postgres-logging-lambda-policy-attachment" {
  policy_arn = aws_iam_policy.postgres-logging-lambda-policy.arn
  role       = aws_iam_role.postgres-logging-lambda-role.name
}

// Attach the policy allowing write access to the Dynamo DB to the lambda
resource "aws_iam_role_policy_attachment" "dynamodb-lambda-policy-attachment" {
  policy_arn = data.aws_iam_policy.dynamodb-put-item-policy.arn
  role       = aws_iam_role.postgres-logging-lambda-role.name
}



// Define the lambda function, 
// -- Bind the code to the lambda
// -- Bind the role to the lambda.
// -- Set environment variables.

resource "aws_lambda_function" "postgres-logging-lambda-function" {
  filename      = "../postgres_logs/lambda.zip"
  function_name = var.postgres_logging_lambda_name
  role          = aws_iam_role.postgres-logging-lambda-role.arn
  handler       = "lambda.lambda_handler"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("../postgres_logs/lambda.zip")
  environment {
    variables = {
      DB_TABLE = data.aws_dynamodb_table.postgreslogs-dynamo-db-table.name
    }
  }

  runtime = "python3.9"
  timeout = 63
  tags    = var.standard_tags
}




//
// Hook up the input -- form clouddwatch  to the function
// ==============================================
// - Identify the cloudwatch log gooup.
// - Identify a "filter" between the log group and our lambda
// - Identify the function in our lambda the event should be sent to.
//  Refernece https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission
//  Referencehttps://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_subscription_filter

resource "aws_cloudwatch_log_subscription_filter" "logging" {
  depends_on      = [aws_lambda_permission.logging]
  destination_arn = aws_lambda_function.postgres-logging-lambda-function.arn
  filter_pattern  = "" #pass everyting 
  log_group_name  = "/aws/rds/instance/scimma-admin-postgres/postgresql"
  name            = "logging_default"
}



// This identifies the cloudwatch log group we will source.
// The log group is not created or managed my this terraform ensemble
// The data statement allows us to get attribute information
// Terraform wll not create/destroy/alter the log groups
data "aws_cloudwatch_log_group" "scimma-admin-postgres-group" {
  name = "/aws/rds/instance/scimma-admin-postgres/postgresql"
}


// Permit the log group to invoke the lambda.
// The log goup is makde by point and click.
// I think when it's suppsrted in terraform we'd make an
//    input.tf and put the data statement (above) in that file
//    and get the ARN in a proper way.
// I've tried a number of permutaions and cannot make it work
// so the  Source ARN is hardwired in.  -- Stll working ou how this data thing works.
// somehow when I give the ARM in plain text. it works.
// using the data statement about, terraform console says the name lacks the terminal ":*"
//      tries many perturbations  but for now, oh well. Gotta figure this out but out of time.
resource "aws_lambda_permission" "logging" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.postgres-logging-lambda-function.function_name
  principal     = "logs.us-west-2.amazonaws.com"
  // does not work source_arn    =  format("%s/%s",data.aws_cloudwatch_log_group.scimma-admin-postgres-group.arn, ":*")
  source_arn = "arn:aws:logs:us-west-2:585193511743:log-group:/aws/rds/instance/scimma-admin-postgres/postgresql:*"
}

//new
resource "aws_cloudwatch_log_subscription_filter" "keycloak-logging" {
  depends_on      = [aws_lambda_permission.keycloak-logging]
  destination_arn = aws_lambda_function.postgres-logging-lambda-function.arn
  filter_pattern  = "" #pass everyting 
  log_group_name  = "/aws/rds/instance/keycloak-test-postgres/postgresql"
  name            = "keycloak_logging_default"
}

resource "aws_lambda_permission" "keycloak-logging" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.postgres-logging-lambda-function.function_name
  principal     = "logs.us-west-2.amazonaws.com"
  // does not work source_arn    =  format("%s/%s",data.aws_cloudwatch_log_group.scimma-admin-postgres-group.arn, ":*")
  source_arn = "arn:aws:logs:us-west-2:585193511743:log-group:/aws/rds/instance/keycloak-test-postgres/postgresql:*"
}

