resource "aws_cloudwatch_event_rule" "listen_summary_event_rule" {
    name                = "trigger-listen-summary-lambda"
    description         = "Trigger Spotify listen summary-generating Lambda once a week"
    schedule_expression = "rate(7 days)"
}

resource "aws_cloudwatch_event_target" "listen_summary_event_target" {
    rule      = aws_cloudwatch_event_rule.listen_summary_event_rule.name
    target_id = "listen_summary_lambda"
    arn       = aws_lambda_function.listen_summary_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda_listen_summary" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.listen_summary_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.listen_summary_event_rule.arn
}