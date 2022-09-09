///
/// 1) setup the lambda
/// 2) Setup periodc running of the lambda


//1_ Setup the lambda
//===================
///
/// 1) setup the lambda
/// 2) Setup periodc running of the lambda

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

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
 
resource "aws_iam_policy" "flow-logging-lambda-policy" {
  name = "Event_trail_S3_purge_allow_policy"

  policy = jsonencode(
  {
  "Version": "2012-10-17",
  "Statement": [
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
    }
)

  tags = var.standard_tags
}



resource "aws_iam_policy" "allow_purge_polcy" {
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



resource "aws_lambda_function" "cludwatch_purge_lambda" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = "lambda.zip"
  function_name = "lambda_handler"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "index.test"

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



/*
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
