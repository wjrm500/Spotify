data "archive_file" "zip_lambda_listen_summary" {
  type        = "zip"
  source_dir = "../lambda/source/listen_summary/"
  output_path = "../lambda/zip/listen_summary.zip"
}

resource "aws_lambda_function" "lambda_listen_summary" {
  filename         = data.archive_file.zip_lambda_listen_summary.output_path
  function_name    = "listen_summary"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "listen_summary.handler"
  source_code_hash = data.archive_file.zip_lambda_listen_summary.output_base64sha256
  runtime          = "python3.8"
  timeout = 120
  depends_on = [
    data.archive_file.zip_lambda_listen_summary
  ]
}