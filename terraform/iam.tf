data "aws_iam_policy_document" "lambda_policy" {
    statement {
        actions    = ["sts:AssumeRole"]
        effect     = "Allow"
        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
    }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_policy.json}"
}

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = "${aws_iam_role.iam_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "aws_iam_policy_document" "ec2" {
    statement {
        actions = [
            "ec2:DescribeNetworkInterfaces",
            "ec2:CreateNetworkInterface",
            "ec2:DeleteNetworkInterface",
            "ec2:DescribeInstances",
            "ec2:AttachNetworkInterface"
        ]
        effect = "Allow"
        resources = ["*"]
  }
}

resource "aws_iam_policy" "ec2" {
    name = "ec2"
    policy = data.aws_iam_policy_document.ec2.json
}