data "aws_network_interface" "inbound_lb_ni" {
  filter {
    name = "vpc-id"
    values = [data.terraform_remote_state.base.outputs.vpc_id]
  }

  filter {
    name = "private-ip-address"
    values = [var.mhs_inbound_lb_ip]
  }
}

resource "aws_cloudwatch_log_group" "inbound_lb_flow_logs" {
  name = "${local.resource_prefix}-inbound_lb_flow_logs"
}

resource "aws_iam_role" "inbound_lb_flow_logs_iam_role" {
  name = "${local.resource_prefix}-inbound_lb_flow_logs_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "vpc-flow-logs.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
  EOF
}

resource "aws_iam_role_policy" "inbound_flow_logs_iam_policy" {
  name = "${local.resource_prefix}-inbound_lb_flow_logs_policy"
  role = aws_iam_role.inbound_lb_flow_logs_iam_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
  EOF
}

resource "aws_flow_log" "inbound_lb_flow_log" {
  traffic_type = "ALL"
  eni_id = data.aws_network_interface.inbound_lb_ni.id
  log_destination = aws_cloudwatch_log_group.inbound_lb_flow_logs.arn
  iam_role_arn = aws_iam_role.inbound_lb_flow_logs_iam_role.arn
}
