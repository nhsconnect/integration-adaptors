resource "aws_security_group" "cloudwatch_sg" { 
  name = "${local.resource_prefix}-cloudwatch_sg"
  description = "Security group controlling access to CloudWatch VPC Endpoint in env: ${var.environment}"
  vpc_id = aws_vpc.base_vpc.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-cloudwatch_sg"
  })
}

resource "aws_security_group" "ecr_sg" {
  name = "${local.resource_prefix}-ecr_sg"
  description = "Security group controlling access to ECR VPC Endpoint in env: ${var.environment}"
  vpc_id = aws_vpc.base_vpc.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-ecr_sg"
  })
}