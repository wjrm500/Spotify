resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  assume_role_policy = <<EOF
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
EOF
}

resource "aws_lambda_function" "test_lambda" {
  filename         = "../test_lambda.zip"
  function_name    = "test_lambda"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "test_lambda.handler"
  source_code_hash = filebase64sha256("../test_lambda.py")
  runtime          = "python3.8"
  environment {
    variables = {
      foo = "bar"
    }
  }
}

data "archive_file" "zip_test_lambda" {
  type        = "zip"
  source_file = "../test_lambda.py"
  output_path = "../test_lambda.zip"
}