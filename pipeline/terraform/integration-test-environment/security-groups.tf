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
  source_security_group_id = aws_security_group.alb_outbound_security_group.id
  description = "HTTP"
}

resource "aws_security_group_rule" "mhs_outbound_security_group_vpc_endpoints_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "S3 and DynamoDb access."
}

resource "aws_security_group_rule" "mhs_outbound_security_group_route_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_route_security_group.id
  description = "HTTP connections to Route service LB."
}

resource "aws_security_group_rule" "mhs_outbound_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

resource "aws_security_group_rule" "mhs_outbound_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
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
  source_security_group_id = aws_security_group.alb_route_security_group.id
  description = "HTTP"
}

resource "aws_security_group_rule" "mhs_route_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
  ]
  description = "S3 access."
}

resource "aws_security_group_rule" "mhs_route_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

resource "aws_security_group_rule" "mhs_route_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
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

resource "aws_security_group_rule" "mhs_inbound_security_group_healthcheck_ingress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "Allow an HTTP connection from the inbound NLB to the inbound service. For LB healthchecks."
}

resource "aws_security_group_rule" "mhs_inbound_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "S3 and DynamoDb access."
}

resource "aws_security_group_rule" "mhs_inbound_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

resource "aws_security_group_rule" "mhs_inbound_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
}

resource "aws_security_group" "ecr_security_group" {
  name = "ECR Endpoint Security Group"
  description = "The security group used to control traffic for the ECR VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id,
      aws_security_group.mhs_route_security_group.id,
      aws_security_group.mhs_inbound_security_group.id
    ]
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
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id,
      aws_security_group.mhs_route_security_group.id,
      aws_security_group.mhs_inbound_security_group.id
    ]
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
      data.aws_vpc.supplier_vpc.cidr_block
    ]
    description = "Inbound HTTP connections"
  }

  egress {
    from_port = 80
    to_port = 80

    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
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
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
    description = "Inbound HTTP connections"
  }

  egress {
    from_port = 80
    to_port = 80

    security_groups = [
      aws_security_group.mhs_route_security_group.id
    ]
    protocol = "tcp"
    description = "Downstream HTTP connections"
  }

  tags = {
    Name = "${var.environment_id}-alb-route-sg"
    EnvironmentId = var.environment_id
  }
}
