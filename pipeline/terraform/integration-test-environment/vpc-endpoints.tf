resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  route_table_ids = [
    aws_vpc.mhs_vpc.main_route_table_id
  ]

  tags = {
    Name = "${var.build_id}-dynamodb-endpoint"
    BuildId = var.build_id
  }
}

resource "aws_vpc_endpoint" "ecr_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true

  security_group_ids = [
    aws_security_group.ecr_security_group.id
  ]

  # An endpoint network interface is created in all of the VPC's subnets.
  subnet_ids = data.aws_subnet_ids.all_in_vpc.ids

  tags = {
    Name = "${var.build_id}-ecr-endpoint"
    BuildId = var.build_id
  }
}

resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = [
    aws_vpc.mhs_vpc.main_route_table_id
  ]

  tags = {
    Name = "${var.build_id}-s3-endpoint"
    BuildId = var.build_id
  }
}

resource "aws_vpc_endpoint" "cloudwatch_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true

  security_group_ids = [
    aws_security_group.cloudwatch_security_group.id
  ]

  # An endpoint network interface is created in all of the VPC's subnets.
  subnet_ids = data.aws_subnet_ids.all_in_vpc.ids

  tags = {
    Name = "${var.build_id}-cloudwatch-endpoint"
    BuildId = var.build_id
  }
}
