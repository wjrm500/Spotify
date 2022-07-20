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
  filename         = "../lambda/zip/load_listens.zip"
  function_name    = "load_listens"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "load_listens.handler"
  source_code_hash = filebase64sha256("../lambda/source/load_listens.py")
  runtime          = "python3.8"
  environment {
    variables = {
      foo = "bar"
    }
  }
}

data "archive_file" "zip_spotify_lambda" {
  type        = "zip"
  source_dir = "../lambda/source/"
  output_path = "../lambda/zip/load_listens.zip"
}