#####################################
# Security groups
#
# This file contains various security groups
# that are used for various things
# (load balancers, VPC endpoints, ECS services, etc)
#####################################


###################
# MHS outbound security group
###################

# MHS outbound security group
resource "aws_security_group" "mhs_outbound_security_group" {
  name = "MHS Outbound Security Group"
  description = "The security group used to control traffic for the MHS Outbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-outbound-sg"
    EnvironmentId = var.environment_id
  }
}

# Ingress rule to allow requests from the MHS outbound load balancer security group
resource "aws_security_group_rule" "mhs_outbound_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_outbound_security_group.id
  description = "Allow HTTP inbound requests from MHS outbound load balancer"
}

# Egress rule to allow requests to S3 (as ECR stores images there and we need to be
# able to get the MHS outbound image to run) and DynamoDB (as MHS outbound uses DynamoDB).
resource "aws_security_group_rule" "mhs_outbound_security_group_vpc_endpoints_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "S3 (for pulling ECR images) and DynamoDb access."
}

# Egress rule to allow requests to the MHS route service load balancer
resource "aws_security_group_rule" "mhs_outbound_security_group_route_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_route_security_group.id
  description = "Allow HTTPS outbound connections to MHS Route service LB."
}

# Egress rule to allow requests to ECR (to pull the MHS outbound image to run)
resource "aws_security_group_rule" "mhs_outbound_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

# Egress rule to allow writing logs to Cloudwatch
resource "aws_security_group_rule" "mhs_outbound_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
}

###################
# MHS route security group
###################

# MHS route service security group
resource "aws_security_group" "mhs_route_security_group" {
  name = "MHS Route Security Group"
  description = "The security group used to control traffic for the MHS Routing component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-route-sg"
    EnvironmentId = var.environment_id
  }
}

# Ingress rule to allow requests from the MHS route load balancer security group
resource "aws_security_group_rule" "mhs_route_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_route_security_group.id
  description = "Allow HTTP inbound requests from MHS route service load balancer"
}

# Egress rule to allow requests to ElastiCache
resource "aws_security_group_rule" "mhs_route_security_group_elasticache_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 6379
  to_port = 6379
  protocol = "tcp"
  source_security_group_id = aws_security_group.sds_cache_security_group.id
  description = "ElastiCache access (for caching SDS query results)."
}

# Egress rule to allow requests to S3 (as ECR stores images there and we need to be
# able to get the MHS route image to run)
resource "aws_security_group_rule" "mhs_route_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
  ]
  description = "S3 access (for pulling ECR images)."
}

# Egress rule to allow requests to ECR (to pull the MHS route image to run)
resource "aws_security_group_rule" "mhs_route_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

# Egress rule to allow writing logs to Cloudwatch
resource "aws_security_group_rule" "mhs_route_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
}

###################
# MHS inbound security group
###################

# MHS inbound security group
resource "aws_security_group" "mhs_inbound_security_group" {
  name = "MHS Inbound Security Group"
  description = "The security group used to control traffic for the MHS Inbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-inbound-sg"
    EnvironmentId = var.environment_id
  }
}

# Ingress rule to allow requests from the MHS inbound load balancer
resource "aws_security_group_rule" "mhs_inbound_security_group_ingress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  # We're allowing inbound requests from the private subnets as MHS inbound load balancer
  # can't have a security group for us to reference.
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "Allow HTTPS inbound requests from MHS inbound load balancer"
}

# Ingress rule to allow healthcheck requests from the MHS inbound load balancer
resource "aws_security_group_rule" "mhs_inbound_security_group_healthcheck_ingress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
  description = "Allow an HTTP connection from the inbound NLB to the inbound service. For LB healthchecks."
}

# Egress rule to allow requests to S3 (as ECR stores images there and we need to be
# able to get the MHS inbound image to run) and DynamoDB (as MHS inbound uses DynamoDB).
resource "aws_security_group_rule" "mhs_inbound_security_group_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [
    aws_vpc_endpoint.s3_endpoint.prefix_list_id,
    aws_vpc_endpoint.dynamodb_endpoint.prefix_list_id]
  description = "S3 (for pulling ECR images) and DynamoDb access."
}

# Egress rule to allow requests to ECR (to pull the MHS inbound image to run)
resource "aws_security_group_rule" "mhs_inbound_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.ecr_security_group.id
  description = "HTTPS connections to ECR endpoint."
}

# Egress rule to allow writing logs to Cloudwatch
resource "aws_security_group_rule" "mhs_inbound_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.mhs_inbound_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.cloudwatch_security_group.id
  description = "HTTPS connections to Cloudwatch endpoint"
}

###################
# VPC endpoint security groups
###################

# Security group for the ECR VPC endpoint
resource "aws_security_group" "ecr_security_group" {
  name = "ECR Endpoint Security Group"
  description = "The security group used to control traffic for the ECR VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    # Only allow incoming requests from MHS security groups
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id,
      aws_security_group.mhs_route_security_group.id,
      aws_security_group.mhs_inbound_security_group.id
    ]
    description = "Allow inbound HTTPS requests from MHS tasks"
  }

  tags = {
    Name = "${var.environment_id}-ecr-endpoint-sg"
    EnvironmentId = var.environment_id
  }
}

# Security group for the Cloudwatch VPC endpoint
resource "aws_security_group" "cloudwatch_security_group" {
  name = "Cloudwatch Endpoint Security Group"
  description = "The security group used to control traffic for the Cloudwatch VPC endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    # Only allow incoming requests from MHS security groups
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id,
      aws_security_group.mhs_route_security_group.id,
      aws_security_group.mhs_inbound_security_group.id
    ]
    description = "Allow inbound HTTPS requests from MHS tasks"
  }

  tags = {
    Name = "${var.environment_id}-cloudwatch-endpoint-sg"
    EnvironmentId = var.environment_id
  }
}

###################
# SDS cache security group
###################

# SDS cache security group
resource "aws_security_group" "sds_cache_security_group" {
  name = "SDS Cache Security Group"
  description = "The security group used to control traffic for the SDS cache endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  ingress {
    from_port = 6379
    to_port = 6379
    protocol = "tcp"
    # Only allow incoming requests from MHS route service security group
    security_groups = [
      aws_security_group.mhs_route_security_group.id
    ]
    description = "Allow Redis requests from MHS route task"
  }

  tags = {
    Name = "${var.environment_id}-sds-cache-sg"
    EnvironmentId = var.environment_id
  }
}

###################
# MHS load balancer security groups
#
# Note that MHS inbound load balancer is a network load balancer
# and network load balancers can't have security groups.
###################


# MHS outbound load balancer security group
resource "aws_security_group" "alb_outbound_security_group" {
  name = "Outbound ALB Security Group"
  description = "The security group used to control traffic for the outbound MHS Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  # Allow inbound traffic from the supplier VPC. We don't make any
  # assumptions here about the internal structure of the supplier VPC,
  # instead just allowing inbound requests from the whole VPC.
  # A supplier could restrict this rule further by limiting access, for
  # example to a specific Security Group
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = [
      data.aws_vpc.supplier_vpc.cidr_block
    ]
    description = "Allow inbound HTTPS connections from supplier VPC"
  }

  # Allow outbound traffic to MHS outbound tasks
  egress {
    from_port = 80
    to_port = 80

    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
    protocol = "tcp"
    description = "Allow downstream HTTP connections to MHS outbound tasks"
  }

  tags = {
    Name = "${var.environment_id}-alb-outbound-sg"
    EnvironmentId = var.environment_id
  }
}

# MHS route load balancer security group
resource "aws_security_group" "alb_route_security_group" {
  name = "Route ALB Security Group"
  description = "The security group used to control traffic for the MHS routing component Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  # Allow inbound traffic from MHS outbound
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
    description = "Allow inbound HTTPS connections from MHS outbound tasks"
  }

  # Allow outbound traffic to MHS route tasks
  egress {
    from_port = 80
    to_port = 80

    security_groups = [
      aws_security_group.mhs_route_security_group.id
    ]
    protocol = "tcp"
    description = "Allow downstream HTTP connections to MHS route tasks"
  }

  tags = {
    Name = "${var.environment_id}-alb-route-sg"
    EnvironmentId = var.environment_id
  }
}
