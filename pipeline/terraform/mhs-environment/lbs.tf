#####################
# Load balancers for MHS ECS services
#####################

##############
# MHS outbound load balancer
##############

# Application load balancer for MHS outbound
resource "aws_lb" "outbound_alb" {
  internal = true
  load_balancer_type = "application"
  subnets = aws_subnet.mhs_subnet.*.id
  security_groups = [
    aws_security_group.alb_outbound_security_group.id
  ]

  access_logs {
    bucket = aws_s3_bucket.mhs_access_logs_bucket.bucket
    prefix = "mhs_outbound-${var.build_id}"
    enabled = true
  }

  # We need the S3 bucket to have the policy set in order for the
  # load balancer to have access to store access logs
  depends_on = [
    aws_s3_bucket_policy.mhs_access_logs_bucket_policy
  ]

  tags = {
    Name = "${var.environment_id}-mhs-outbound-alb"
    EnvironmentId = var.environment_id
  }
}

# Target group for the application load balancer for MHS outbound
# The MHS outbound ECS service registers it's tasks here.
resource "aws_lb_target_group" "outbound_alb_target_group" {
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = aws_vpc.mhs_vpc.id

  health_check {
    path = "/healthcheck"
    matcher = "200"
    healthy_threshold = var.healthcheck_threshold
    unhealthy_threshold = var.healthcheck_threshold
  }

  deregistration_delay = var.lb_deregistration_delay

  tags = {
    Name = "${var.environment_id}-mhs-outbound-alb-target-group"
    EnvironmentId = var.environment_id
  }
}

# Terraform output variable of the MHS outbound load balancer's target group ARN
output "outbound_lb_target_group_arn" {
  value = aws_lb_target_group.outbound_alb_target_group.arn
  description = "The ARN of the MHS outbound service load balancers's target group."
}

# Listener for MHS outbound load balancer that forwards requests to the correct target group
resource "aws_lb_listener" "outbound_alb_listener" {
  load_balancer_arn = aws_lb.outbound_alb.arn
  port = 443
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn = var.outbound_alb_certificate_arn

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.outbound_alb_target_group.arn
  }
}

##############
# MHS route load balancer
##############

# Application load balancer for MHS route service
resource "aws_lb" "route_alb" {
  internal = true
  load_balancer_type = "application"
  subnets = aws_subnet.mhs_subnet.*.id
  security_groups = [
    aws_security_group.alb_route_security_group.id
  ]

  access_logs {
    bucket = aws_s3_bucket.mhs_access_logs_bucket.bucket
    prefix = "mhs_route-${var.build_id}"
    enabled = true
  }

  # We need the S3 bucket to have the policy set in order for the
  # load balancer to have access to store access logs
  depends_on = [
    aws_s3_bucket_policy.mhs_access_logs_bucket_policy
  ]

  tags = {
    Name = "${var.environment_id}-mhs-route-alb"
    EnvironmentId = var.environment_id
  }
}

# Target group for the application load balancer for MHS route service
# The MHS route ECS service registers it's tasks here.
resource "aws_lb_target_group" "route_alb_target_group" {
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = aws_vpc.mhs_vpc.id

  health_check {
    path = "/healthcheck"
    matcher = "200"
    healthy_threshold = var.healthcheck_threshold
    unhealthy_threshold = var.healthcheck_threshold
  }

  deregistration_delay = var.lb_deregistration_delay

  tags = {
    Name = "${var.environment_id}-mhs-route-alb-target-group"
    EnvironmentId = var.environment_id
  }
}

# Terraform output variable of the MHS route service's load balancer's target group ARN
output "route_lb_target_group_arn" {
  value = aws_lb_target_group.route_alb_target_group.arn
  description = "The ARN of the MHS Spine route lookup service load balancers's target group."
}

# Listener for MHS route service's load balancer that forwards requests to the correct target group
resource "aws_lb_listener" "route_alb_listener" {
  load_balancer_arn = aws_lb.route_alb.arn
  port = 443
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn = var.route_alb_certificate_arn

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.route_alb_target_group.arn
  }
}

##############
# MHS inbound load balancer
##############

# Network load balancer for MHS inbound.
# MHS inbound tasks handle the TLS termination as they do TLS MA. This is why we
# have to use a network load balancer here and not an application load balancer,
# to passthrough the SSL traffic.
resource "aws_lb" "inbound_nlb" {
  internal = true
  load_balancer_type = "network"
  subnets = aws_subnet.mhs_subnet.*.id
  enable_cross_zone_load_balancing = true

  access_logs {
    bucket = aws_s3_bucket.mhs_access_logs_bucket.bucket
    prefix = "mhs_inbound-${var.build_id}"
    enabled = true
  }

  # We need the S3 bucket to have the policy set in order for the
  # load balancer to have access to store access logs
  depends_on = [
    aws_s3_bucket_policy.mhs_access_logs_bucket_policy
  ]

  tags = {
    Name = "${var.environment_id}-mhs-inbound-nlb"
    EnvironmentId = var.environment_id
  }
}

# Target group for the network load balancer for MHS inbound
# The MHS inbound ECS service registers it's tasks here.
resource "aws_lb_target_group" "inbound_nlb_target_group" {
  port = 443
  protocol = "TCP"
  target_type = "ip"
  vpc_id = aws_vpc.mhs_vpc.id

  health_check {
    protocol = "HTTP"
    port = 80
    path = "/healthcheck"
    healthy_threshold = var.healthcheck_threshold
    unhealthy_threshold = var.healthcheck_threshold
  }

  deregistration_delay = var.lb_deregistration_delay

  tags = {
    Name = "${var.environment_id}-mhs-inbound-nlb-target-group"
    EnvironmentId = var.environment_id
  }
}

# Terraform output variable of the MHS inbound load balancer's target group ARN
output "inbound_lb_target_group_arn" {
  value = aws_lb_target_group.inbound_nlb_target_group.arn
  description = "The ARN of the MHS inbound service load balancers's target group."
}

# Listener for MHS inbound load balancer that forwards requests to the correct target group
resource "aws_lb_listener" "inbound_nlb_listener" {
  load_balancer_arn = aws_lb.inbound_nlb.arn
  port = 443
  protocol = "TCP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.inbound_nlb_target_group.arn
  }
}
