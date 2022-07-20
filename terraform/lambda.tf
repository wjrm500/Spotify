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

data "archive_file" "zip_lambda_load_listens" {
  type        = "zip"
  source_dir = "../lambda/source/"
  output_path = "../lambda/zip/load_listens.zip"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  assume_role_policy = "${data.aws_iam_policy_document.AWSLambdaTrustPolicy.json}"
}

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = "${aws_iam_role.iam_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "lambda_load_listens" {
  filename         = "../lambda/zip/load_listens.zip"
  function_name    = "load_listens"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "load_listens.handler"
  source_code_hash = "${data.archive_file.zip_lambda_load_listens.output_base64sha256}"
  runtime          = "python3.8"
  environment {
    variables = {
      DB_HOST     = var.DB_HOST,
      DB_PORT     = var.DB_PORT,
      DB_USER     = var.DB_USER,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
}

