resource "aws_security_group" "mhs_outbound_security_group" {
  name = "MHS Outbound Security Group"
  description = "The security group used to control traffic for the MHS Outbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-outbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "mhs_route_security_group" {
  name = "MHS Route Security Group"
  description = "The security group used to control traffic for the MHS Routing component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-route-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "mhs_inbound_security_group" {
  name = "MHS Inbound Security Group"
  description = "The security group used to control traffic for the MHS Inbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-inbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "ecr_security_group" {
  name = "ECR Endpoint Security Group"
  description = "The security group used to control traffic for the ECR VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = data.aws_subnet.all_in_vpc.*.cidr_block
    description = "HTTPS"
  }

  tags = {
    Name = "${var.build_id}-ecr-endpoint-sg"
    BuildId = var.build_id
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
    cidr_blocks = data.aws_subnet.all_in_vpc.*.cidr_block
    description = "HTTPS"
  }

  egress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = data.aws_subnet.all_in_vpc.*.cidr_block
    description = "HTTPS"
  }

  tags = {
    Name = "${var.build_id}-cloudwatch-endpoint-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "sds_cache_security_group" {
  name = "SDS Cache Security Group"
  description = "The security group used to control traffic for the SDS cache endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-sds-cache-sg"
    BuildId = var.build_id
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

  tags = {
    Name = "${var.build_id}-alb-outbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "alb_route_security_group" {
  name = "Route ALB Security Group"
  description = "The security group used to control traffic for the MHS routing component Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-alb-route-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "alb_inbound_security_group" {
  name = "Inbound ALB Security Group"
  description = "The security group used to control traffic for the inbound MHS Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-alb-inbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "async_response_queue_security_group" {
  name = "Async Response Queue Security Group"
  description = "The security group used to control traffic for the asynchronous response queue endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-async-response-queue-sg"
    BuildId = var.build_id
  }
}
