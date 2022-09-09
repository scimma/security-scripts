///
/// 1) setup the lambda
/// 2) Setup periodic running of the lambda


//1_ Setup the lambda
//===================
///
/// 1) setup the lambda
/// 2) Setup periodc running of the lambda

resource "aws_iam_role" "cloudwatch_s3_purge_lambda_role" {
  name = "cloudwatch_s3_purge_lambda_role"

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


// Make  a policy allowing the lambda function to log itself
// and to purge stuff in the S3 bucket(scimma-proccesses)

resource "aws_iam_policy" "cloudwatch_s3_lambda_logging_policy" {
  name = "cloudwatch_s3_lambda_logging_policy"

  policy = jsonencode(
  {
  "Version": "2012-10-17",
  "Statement": [
    {
         "Action" : [
          "logs:CreateLogGroup",
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


resource "aws_iam_policy" "cloudwatch_s3_lambda_purge_policy" {
  name = "cloudwatch_s3_lambda_purge_policy"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
         "Action": [
            "s3:ListBucketMultipartUploads",
            "s3:DeleteObjectVersion",
            "s3:ListBucket",
            "s3:DeleteObject"
          ],
          "Resource": "arn:aws:s3:::scimma-processes"
     }]}
     )

  tags = var.standard_tags
}

// Attach the policys  allowing logging the lambda itself to lambda's role

resource "aws_iam_role_policy_attachment" "purge-policy-attachment" {
  policy_arn = aws_iam_policy.cloudwatch_s3_lambda_purge_policy.arn
  role       = aws_iam_role.cloudwatch_s3_purge_lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_logging_policy" {
  policy_arn = aws_iam_policy.cloudwatch_s3_lambda_logging_policy.arn
  role       = aws_iam_role.cloudwatch_s3_purge_lambda_role.name
}


resource "aws_lambda_function" "cloudwatch_s3_purge_lambda" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = "lambda.zip"
  function_name = "cloudwatch_s3_purge_prod"
  role          = aws_iam_role.cloudwatch_s3_purge_lambda_role.arn
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
}


/**********

//2)  Setup periodic stimulatipn of thelambda.
//============================================

resource "aws_cloudwatch_event_rule" "opsec-daily-event" {
  name                = "opsec-daily-event"
  description         = "Fires once per day"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "purge_cloudtrail_each_day" {
  rule      = aws_cloudwatch_event_rule.opsec-daily-even.name
  target_id = "lambda"
  arn       = aws_lambda_function.lambda.arn
}


resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_daily" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.opsec-daily-even.arn}"
  
}
*/
