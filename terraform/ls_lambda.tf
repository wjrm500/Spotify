data "archive_file" "zip_listen_summary_lambda" {
  type        = "zip"
  source_dir = "../lambda/source/listen_summary/"
  output_path = "../lambda/zip/listen_summary.zip"
}

resource "aws_lambda_function" "listen_summary_lambda" {
  filename         = data.archive_file.zip_listen_summary_lambda.output_path
  function_name    = "listen_summary"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "listen_summary.handler"
  source_code_hash = data.archive_file.zip_listen_summary_lambda.output_base64sha256
  runtime          = "python3.8"
  timeout = 120
  depends_on = [
    data.archive_file.zip_listen_summary_lambda
  ]
}