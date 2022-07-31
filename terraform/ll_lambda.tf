data "archive_file" "zip_load_listens_lambda" {
  type        = "zip"
  source_dir = "../lambda/source/load_listens/"
  output_path = "../lambda/zip/load_listens.zip"
}

data "archive_file" "zip_load_listens_layer" {
  type        = "zip"
  source_dir = "../lambda/dependencies/"
  output_path = "../lambda/zip/layer.zip"
}

resource "aws_lambda_layer_version" "load_listens_layer" {
  filename   = "../lambda/zip/layer.zip"
  layer_name = "layer"
  compatible_runtimes = ["python3.8"]
  source_code_hash = "${data.archive_file.zip_load_listens_layer.output_base64sha256}"
  depends_on = [
    data.archive_file.zip_load_listens_layer
  ]
}

resource "aws_lambda_function" "load_listens_lambda" {
  filename         = data.archive_file.zip_load_listens_lambda.output_path
  function_name    = "load_listens"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "load_listens.handler"
  source_code_hash = data.archive_file.zip_load_listens_lambda.output_base64sha256
  runtime          = "python3.8"
  layers = [aws_lambda_layer_version.load_listens_layer.arn]
  timeout = 120
  depends_on = [
    data.archive_file.zip_load_listens_lambda
  ]
}