resource "aws_security_group" "mhs_outbound_security_group" {
  name = "MHS Outbound Security Group"
  description = "The security group used to control traffic for the MHS Outbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-outbound-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group_rule" "mhs_outbound_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "HTTP"
}

resource "aws_security_group_rule" "mhs_outbound_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "HTTPS"
}

resource "aws_security_group" "mhs_route_security_group" {
  name = "MHS Route Security Group"
  description = "The security group used to control traffic for the MHS Routing component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-route-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group_rule" "mhs_route_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "HTTP"
}

resource "aws_security_group_rule" "mhs_route_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "HTTPS"
}

resource "aws_security_group" "mhs_inbound_security_group" {
  name = "MHS Inbound Security Group"
  description = "The security group used to control traffic for the MHS Inbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-inbound-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group_rule" "mhs_inbound_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "HTTPS"
}

resource "aws_security_group_rule" "mhs_inbound_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "HTTPS"
}

resource "aws_security_group" "ecr_security_group" {
  name = "ECR Endpoint Security Group"
  description = "The security group used to control traffic for the ECR VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
    description = "HTTPS"
  }

  tags = {
    Name = "${var.environment_id}-ecr-endpoint-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "cloudwatch_security_group" {
  name = "Cloudwatch Endpoint Security Group"
  description = "The security group used to control traffic for the Cloudwatch VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
    description = "HTTPS"
  }

  egress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
    description = "HTTPS"
  }

  tags = {
    Name = "${var.environment_id}-cloudwatch-endpoint-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "sds_cache_security_group" {
  name = "SDS Cache Security Group"
  description = "The security group used to control traffic for the SDS cache endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-sds-cache-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "alb_outbound_security_group" {
  name = "Outbound ALB Security Group"
  description = "The security group used to control traffic for the outbound MHS Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    description = "Inbound HTTP connections"
  }

  egress {
    from_port = 80
    to_port = 80

    cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
    protocol = "tcp"
    description = "Downstream HTTP connections"
  }

  tags = {
    Name = "${var.environment_id}-alb-outbound-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "alb_route_security_group" {
  name = "Route ALB Security Group"
  description = "The security group used to control traffic for the MHS routing component Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    description = "Inbound HTTP connections"
  }

  egress {
    from_port = 80
    to_port = 80

    cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
    protocol = "tcp"
    description = "Downstream HTTP connections"
  }

  tags = {
    Name = "${var.environment_id}-alb-route-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "async_response_queue_security_group" {
  name = "Async Response Queue Security Group"
  description = "The security group used to control traffic for the asynchronous response queue endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-async-response-queue-sg"
    EnvironmentId = var.environment_id
  }
}
