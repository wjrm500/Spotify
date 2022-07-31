resource "aws_sns_topic" "send_email_topic" {
  name = "send-email-topic"
}

resource "aws_sns_topic_subscription" "send_email_topic_subscription" {
  topic_arn = aws_sns_topic.send_email_topic.arn
  protocol  = "email"
  endpoint  = var.email
}