# DynamoDB VPC endpoint
resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id = aws_vpc.base_vpc.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  route_table_ids = [
    aws_vpc.base_vpc.main_route_table_id,
    aws_route_table.private.id
  ]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-dynamodb-vpce"
  })
}

# ECR DKR VPC endpoint
resource "aws_vpc_endpoint" "ecr_endpoint" {
  vpc_id = aws_vpc.base_vpc.id
  service_name = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true
  security_group_ids = [
    aws_security_group.ecr_sg.id
  ]
  subnet_ids = [aws_subnet.base_subnet.id]
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-ecr-vpce"
  })
}

resource "aws_vpc_endpoint" "ecr_api_endpoint" {
  vpc_id = aws_vpc.base_vpc.id
  service_name = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true
  security_group_ids = [
    aws_security_group.ecr_sg.id
  ]
  subnet_ids = [aws_subnet.base_subnet.id]
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-ecr-api-vpce"
  })
}

# S3 VPC endpoint
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id = aws_vpc.base_vpc.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = [
    aws_vpc.base_vpc.main_route_table_id,
    aws_route_table.private.id
  ]
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-s3-vpce"
  })
}

# Cloudwatch VPC endpoint
resource "aws_vpc_endpoint" "cloudwatch_endpoint" {
  vpc_id = aws_vpc.base_vpc.id
  service_name = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true
  security_group_ids = [
    aws_security_group.cloudwatch_sg.id
  ]
  subnet_ids = [aws_subnet.base_subnet.id]
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-cloudwatch-vpce"
  })
}
