//0 Keep track of terraform state in AWS
//  So that we are not realyin gon nayone's laptop.


terraform {
    backend "s3" {
    bucket = "scimma-processes-us-west-2"
    key    = "tfstate/purgers/prod"
    region = "us-west-2"
  }
}
///
/// 1) setup the lambda
/// 2) Setup periodic running of the lambda


//1_ Setup the lambda
//===================
///
/// 1) setup the lambda
/// 2) Setup periodic running of the lambda


//1.1 Make a role to hang all the permissions on
//----------------------------------------------

resource "aws_iam_role" "opsec-cloudwatch-s3-purge-lambda_role" {
  name = "opsec-cloudwatch-s3-purge-lambda_role"

  assume_role_policy = jsonencode(
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
     ]
  }
)
  tags = var.standard_tags
}

//1.2  Make usable resources so the lambda can log itself.
//----------------------------------------------------------
// 1.2.1  Make a cloudwatch log group for the lambd's own logging.
//        e.g record outptu from its handler, print and python logging
//        AWS would make this, but we dont want the default infinite retention.
resource "aws_cloudwatch_log_group" "function_log_group" {
  name              = format("%s/%s",
                             "/aws/lambda",
                             aws_lambda_function.opsec-cloudwatch-s3-purge-lambda.function_name
                             )
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
  tags = var.standard_tags
}

// 1.2.2 Make  a policy permitting the lambda function use to the
//         log group above.
resource "aws_iam_policy" "cloudwatch_s3_lambda_logging_policy" {
  name = "cloudwatch_s3_lambda_logging_policy"
  
  policy = jsonencode(
  {
  "Version": "2012-10-17",
  "Statement": [
    {
         "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Effect" : "Allow",
        "Resource" : "arn:aws:logs:*:*:*"
    }
    ]
    }
)

  tags = var.standard_tags
}

// 1.2.3 Attach the policy to the Role the lamda would use.

resource "aws_iam_role_policy_attachment" "lambda_logging_policy" {
  policy_arn = aws_iam_policy.cloudwatch_s3_lambda_logging_policy.arn
  role       = aws_iam_role.opsec-cloudwatch-s3-purge-lambda_role.name
}


// 1.3  Give the lambda permission to purge the bucket
// ---------------------------------------------------

// 1.3.1 make permissions to
//       - list the bucket
//       - delete objects 
resource "aws_iam_policy" "cloudwatch_s3_lambda_purge_policy" {
  name = "cloudwatch_s3_lambda_purge_policy"
  policy = jsonencode({
    "Statement": [
        {
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::scimma-processes/*"
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::scimma-processes"
        }
    ],
    "Version": "2012-10-17"
}
)


  tags = var.standard_tags
}

// 1.3.1 attach the permissions to the lamba's rome 

resource "aws_iam_role_policy_attachment" "purge-policy-attachment" {
  policy_arn = aws_iam_policy.cloudwatch_s3_lambda_purge_policy.arn
  role       = aws_iam_role.opsec-cloudwatch-s3-purge-lambda_role.name
}



// 1.4 Make the lambda function itself
// -----------------------------------

// 1.4.1  Define the lambda
//        
resource "aws_lambda_function" "opsec-cloudwatch-s3-purge-lambda" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = "lambda.zip"
  function_name = "opsec-cloudwatch-s3-purge-prod"
  role          = aws_iam_role.opsec-cloudwatch-s3-purge-lambda_role.arn
  handler       = "lambda.lambda_handler"
  timeout       = 120

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("lambda.zip")

  runtime = "python3.9"

  environment {
    variables = {
      foo = "bar"
    }
  }
    tags = var.standard_tags
}



//2)  Setup periodic execution of the lambda.
//    =======================================


//2.1 -- use existing daily event 
resource  "aws_cloudwatch_event_rule" "daily-event" {
  name                = "opsec-daily"
  schedule_expression = "cron(0 12 * * ? *)"
  tags = var.standard_tags
}

// 2.2 -- set our lambda  as the target.
resource "aws_cloudwatch_event_target" "purge_cloudtrail_each_day" {
  rule      = aws_cloudwatch_event_rule.daily-event.name
  target_id = "lambda"
  arn       = aws_lambda_function.opsec-cloudwatch-s3-purge-lambda.arn
}

// 2.3 -- Give the event permission to invode the lambda.
resource "aws_lambda_permission" "opsec-allow-daily-execution" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.opsec-cloudwatch-s3-purge-lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily-event.arn
}

