###################
# VPC endpoints
#
# The MHS VPC does not have public ip addresses,
# so in order to access various AWS services, we
# need to have some VPC endpoints. This keeps
# traffic to AWS services within the AWS network.
###################

# DynamoDB VPC endpoint
resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  route_table_ids = [
    aws_vpc.mhs_vpc.main_route_table_id
  ]

  tags = {
    Name = "${var.environment_id}-dynamodb-endpoint"
    EnvironmentId = var.environment_id
  }
}

# ECR VPC endpoint
resource "aws_vpc_endpoint" "ecr_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true

  security_group_ids = [
    aws_security_group.ecr_security_group.id
  ]

  # An endpoint network interface is created in all of the subnets we have created.
  subnet_ids = aws_subnet.mhs_subnet.*.id

  tags = {
    Name = "${var.environment_id}-ecr-endpoint"
    EnvironmentId = var.environment_id
  }
}

# S3 VPC endpoint
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = [
    aws_vpc.mhs_vpc.main_route_table_id
  ]

  tags = {
    Name = "${var.environment_id}-s3-endpoint"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch VPC endpoint
resource "aws_vpc_endpoint" "cloudwatch_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true

  security_group_ids = [
    aws_security_group.cloudwatch_security_group.id
  ]

  # An endpoint network interface is created in all of the subnets we have created.
  subnet_ids = aws_subnet.mhs_subnet.*.id

  tags = {
    Name = "${var.environment_id}-cloudwatch-endpoint"
    EnvironmentId = var.environment_id
  }
}
