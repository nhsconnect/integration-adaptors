# CloudWatch
resource "aws_security_group_rule" "core_sg_to_cloudwatch_sg" { 
  type      = "egress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id        = aws_security_group.core_sg.id
  source_security_group_id = aws_security_group.cloudwatch_sg.id
}

resource "aws_security_group_rule" "cloudwatch_sg_from_core_sg" { 
  type      = "ingress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id        = aws_security_group.cloudwatch_sg.id
  source_security_group_id = aws_security_group.core_sg.id
}

# ECR
resource "aws_security_group_rule" "core_sg_to_ecr_sg" { 
  type      = "egress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id        = aws_security_group.core_sg.id
  source_security_group_id = aws_security_group.ecr_sg.id
}

resource "aws_security_group_rule" "ecr_sg_from_core_sg" { 
  type      = "ingress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id        = aws_security_group.ecr_sg.id
  source_security_group_id = aws_security_group.core_sg.id
}

# S3
resource "aws_security_group_rule" "core_sg_to_s3_prefix" { 
  type      = "egress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id = aws_security_group.core_sg.id
  prefix_list_ids = [aws_vpc_endpoint.s3_endpoint.prefix_list_id]
}

# DynamoDB
resource "aws_security_group_rule" "core_sg_to_dynamodb_prefix" { 
  type      = "egress"
  from_port = 443
  to_port   = 443
  protocol  = "tcp"
  security_group_id = aws_security_group.core_sg.id
  prefix_list_ids  = [aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
}