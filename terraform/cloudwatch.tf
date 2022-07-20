resource "aws_cloudwatch_event_rule" "every_12_hours" {
    name                = "every_12_hours"
    description         = "Fires every 12 hours"
    schedule_expression = "rate(5 minutes)" // Change to 12 hours - set to 5 minutes for testing purposes
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
    rule      = aws_cloudwatch_event_rule.every_12_hours.name
    target_id = "lambda_load_listens"
    arn       = aws_lambda_function.lambda_load_listens.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_load_listens.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.every_12_hours.arn
}