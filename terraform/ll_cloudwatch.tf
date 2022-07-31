resource "aws_cloudwatch_event_rule" "load_listens_event_rule" {
    name                = "trigger-load-listens-lambda"
    description         = "Trigger Spotify listen-logging Lambda every X hours"
    schedule_expression = "rate(3 hours)"
}

resource "aws_cloudwatch_event_target" "load_listens_event_target" {
    rule      = aws_cloudwatch_event_rule.load_listens_event_rule.name
    target_id = "load_listens_lambda"
    arn       = aws_lambda_function.load_listens_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_load_listens" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.load_listens_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.load_listens_event_rule.arn
}

resource "aws_cloudwatch_metric_alarm" "load_listens_failed" {
  alarm_name                = "load-listens-failed"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = "86400" # 1 day
  statistic                 = "Average"
  threshold                 = "1"
  alarm_description         = "This alarm checks if the Spotify Lambda failed in the last day"
  alarm_actions             = [aws_sns_topic.send_email_topic.arn]
  dimensions                = {
    function_name = aws_lambda_function.load_listens_lambda.function_name
  }
}