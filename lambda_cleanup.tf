# IAM role for Lambda execution
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_cleanup_role" {
  role = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_cleanup_policy.arn
}

resource "aws_iam_policy" "lambda_cleanup_policy" {
  name        = "lambda_cleanup_policy"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action = [
          "ec2:DescribeRegions",
          "ec2:DescribeAddresses",
          "ec2:ReleaseAddress",
          "ec2:DescribeVolumes",
          "ec2:DeleteVolume",
          "ec2:DescribeSnapshots",
          "ec2:DeleteSnapshot"
        ]
        Resource = "*"
      },
      {  
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Package the Lambda function code
data "archive_file" "lambda_code_package" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda function
resource "aws_lambda_function" "lambda_cleanup_function" {
  filename      = data.archive_file.lambda_code_package.output_path
  function_name = "lambda_cleanup_function"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash    = data.archive_file.lambda_code_package.output_base64sha256
  timeout = 300

  runtime = "python3.14"

  environment {
    variables = {
       "DRY_RUN" = "TRUE"
    }
  }
}

resource "aws_cloudwatch_event_rule" "cleanup_rule" {
  name = "cleanup_rule"
  description = "Cleanup performed on monday"
  schedule_expression = "cron(0 0 ? * MON *)"
}

resource "aws_cloudwatch_event_target" "cleanup_target" {
  rule = aws_cloudwatch_event_rule.cleanup_rule.name
  arn = aws_lambda_function.lambda_cleanup_function.arn
}

resource "aws_lambda_permission" "event_bridge_rule" {
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_cleanup_function.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.cleanup_rule.arn
}