# Ingress rule to allow requests from the fake-spine load balancer security group
resource "aws_security_group_rule" "fake_spine_security_group_ingress_80" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_fake_spine_security_group.id
  description = "Allow HTTP inbound requests from fake spine load balancer"
}

resource "aws_security_group_rule" "fake_spine_security_group_ingress_443" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb_fake_spine_security_group.id
  description = "Allow HTTP inbound requests from fake spine load balancer"
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_80" {
  security_group_id = aws_security_group.alb_fake_spine_security_group.id
  source_security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  description = "Allow HTTP from ALB SG to fake spine service"
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_443" {
  security_group_id = aws_security_group.alb_fake_spine_security_group.id
  source_security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  description = "Allow HTTP from ALB SG to fake spine service"
}

# Egress rule to allow requests to S3 (as ECR stores images there and we need to be
# able to get the MHS outbound image to run)
resource "aws_security_group_rule" "fake_spine_security_group_vpc_endpoints_egress_rule" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  prefix_list_ids = [data.terraform_remote_state.mhs.outputs.s3_endpoint_prefix_list_ids]
  description = "S3 (for pulling ECR images)"
}

# Egress rule to allow requests to the MHS inbound service load balancer is it needed?
# resource "aws_security_group_rule" "fake_spine_security_group_route_egress_rule" {
#   security_group_id = aws_security_group.fake_spine_security_group.id
#   type = "egress"
#   from_port = 443
#   to_port = 443
#   protocol = "tcp"
#   source_security_group_id = aws_security_group.alb_mhs_inbound_security_group.id
#   description = "Allow HTTPS outbound connections to MHS Route service LB."
# }

# Egress rule to allow requests to ECR (to pull the MHS outbound image to run)
# resource "aws_security_group_rule" "fake_spine_security_group_ecr_egress_rule" {
#   security_group_id = aws_security_group.fake_spine_security_group.id
#   type = "egress"
#   from_port = 443
#   to_port = 443
#   protocol = "tcp"
#   source_security_group_id = data.terraform_remote_state.mhs.outputs.ecr_vpce_security_group_id
#   description = "HTTPS connections to ECR endpoint."
# }

# # # Egress rule to allow writing logs to Cloudwatch
# resource "aws_security_group_rule" "fake_spine_security_group_cloudwatch_egress_rule" {
#   security_group_id = aws_security_group.fake_spine_security_group.id
#   type = "egress"
#   from_port = 443
#   to_port = 443
#   protocol = "tcp"
#   //source_security_group_id = aws_security_group.cloudwatch_security_group.id
#   source_security_group_id = data.terraform_remote_state.mhs.outputs.cloudwatch_vpce_security_group_id
#   description = "HTTPS connections to Cloudwatch endpoint"
# }
