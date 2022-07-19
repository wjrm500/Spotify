data "aws_iam_policy_document" "AWSLambdaTrustPolicy" {
  statement {
    actions    = ["sts:AssumeRole"]
    effect     = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  assume_role_policy = "${data.aws_iam_policy_document.AWSLambdaTrustPolicy.json}"
}

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = "${aws_iam_role.iam_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "spotify_lambda" {
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

data "archive_file" "zip_spotify_lambda" {
  type        = "zip"
  source_file = "../test_lambda.py"
  output_path = "../test_lambda.zip"
}