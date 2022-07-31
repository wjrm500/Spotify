resource "aws_cloudwatch_event_rule" "trigger_spotify_lambda" {
    name                = "trigger-spotify-lambda"
    description         = "Trigger Spotify listen-logging Lambda every X hours"
    schedule_expression = "rate(3 hours)"
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
    rule      = aws_cloudwatch_event_rule.trigger_spotify_lambda.name
    target_id = "lambda_load_listens"
    arn       = aws_lambda_function.lambda_load_listens.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_load_listens.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.trigger_spotify_lambda.arn
}

resource "aws_cloudwatch_metric_alarm" "spotify_lambda_failed" {
  alarm_name                = "spotify-lambda-failed"
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
    function_name = aws_lambda_function.lambda_load_listens.function_name
  }
}