data "archive_file" "zip_lambda_load_listens" {
  type        = "zip"
  source_dir = "../lambda/source/"
  output_path = "../lambda/zip/load_listens.zip"
}

data "archive_file" "zip_lambda_layer" {
  type        = "zip"
  source_dir = "../lambda/dependencies/"
  output_path = "../lambda/zip/layer.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "../lambda/zip/layer.zip"
  layer_name = "layer"
  compatible_runtimes = ["python3.8"]
}

resource "aws_lambda_function" "lambda_load_listens" {
  filename         = "../lambda/zip/load_listens.zip"
  function_name    = "load_listens"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "load_listens.handler"
  source_code_hash = "${data.archive_file.zip_lambda_load_listens.output_base64sha256}"
  runtime          = "python3.8"
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  environment {
    variables = {
      DB_HOST     = var.DB_HOST,
      DB_PORT     = var.DB_PORT,
      DB_USER     = var.DB_USER,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
  vpc_config {
    subnet_ids         = var.VPC_SUBNET_IDS
    security_group_ids = var.VPC_SECURITY_GROUP_IDS
  }
  timeout = 5
}