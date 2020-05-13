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

resource "aws_security_group_rule" "fake_spine_security_group_ecr_egress_rule" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = data.terraform_remote_state.mhs.outputs.ecr_vpce_security_group_id
  description = "HTTPS connections to ECR endpoint."
}

# # Egress rule to allow writing logs to Cloudwatch
resource "aws_security_group_rule" "fake_spine_security_group_cloudwatch_egress_rule" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  source_security_group_id = data.terraform_remote_state.mhs.outputs.cloudwatch_vpce_security_group_id
  description = "HTTPS connections to Cloudwatch endpoint"
}

aws_security_group_rule "cloudwatch_sg_ingress_fakespine" {
  security_group_id = data.terraform_remote_state.mhs.outputs.cloudwatch_vpce_security_group_id
  from_port = 443
  to_port = 443
  protocol = "tcp"
  type = "ingress"
  source_security_group_id = aws_security_group.fake_spine_security_group.id
  description = "Allow MHS route to cloudwatch"
}

resource "aws_security_group_rule" "fake_spine_security_group_ingress_22" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["91.222.71.98/32", "62.254.63.52/32"]
  description = "Allow SSH inbound from Kainos VPN"
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_Internet_443" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  description = "HTTPS connections to Internet."
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_Internet_80" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  description = "HTTPS connections to Internet."
}

# As we do not use loadbalancer, we allow FS SG to talk with MHS inbound and outbound

# mhs outbound -> fake-spine
resource "aws_security_group_rule" "fake_spine_sg_ingress_outbound_app_port" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = data.terraform_remote_state.mhs.outputs.outbound_sg_id
  description = "Allow ingress ${var.fake_spine_port} inbound requests from MHS outbound"
}

resource "aws_security_group_rule" "fake_spine_security_sg_egress_outbound_app_port" {
  security_group_id = data.terraform_remote_state.mhs.outputs.outbound_sg_id
  type = "egress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = aws_security_group.fake_spine_security_group.id
  description = "Allow egress ${var.fake_spine_port} inbound requests from MHS outbound"
}

# vp jumbbox -> fake-spine
resource "aws_security_group_rule" "fake_spine_sg_ingress_jumpbox_app_port" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  cidr_blocks = ["172.31.16.204/32"]
  description = "Allow ingress ${var.fake_spine_port} inbound requests from VP jumpbox"
}

# fake-spine -> mhs inbound
# ingress lb does not have a security group, allowing traffic within the subnet
resource "aws_security_group_rule" "fake_spine_security_sg_egress_inbound_app_port" {
  security_group_id = aws_security_group.fake_spine_security_group.id 
  type = "egress"
  from_port = var.mhs_inbound_port
  to_port = var.mhs_inbound_port
  protocol = "tcp"
  cidr_blocks = data.terraform_remote_state.mhs.outputs.subnet_cidrs
  # source_security_group_id = data.terraform_remote_state.mhs.outputs.inbound_lb_sg_id
  description = "Allow egress ${var.fake_spine_port} outbound requests to MHS inbound"
}

# resource "aws_security_group_rule" "fake_spine_security_group_ingress_443" {
#   security_group_id = data.terraform_remote_state.mhs.outputs.inbound_lb_sg_id
#   type = "ingress"
#   from_port = var.mhs_inbound_port
#   to_port = var.mhs_inbound_port
#   protocol = "tcp"
#   cidr_blocks = aws_subnet.mhs_subnet.*.cidr_block
#   source_security_group_id = aws_security_group.fake_spine_security_group.id
#   description = "Allow ingress ${var.fake_spine_port} inbound requests on MHS inbound"
# }


# For fake spine load balancer

# Allow connection from load balancer to fake spine instances

resource "aws_security_group_rule" "instance_from_fake_spine_alb" {
  security_group_id = aws_security_group.fake_spine_security_group.id 
  type = "ingress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = aws_security_group.fake_spine_alb_security_group.id
  description = "Allow ingress ${var.fake_spine_port} on application from LB"
}

resource "aws_security_group_rule" "fake_spine_alb_to_instance" {
  security_group_id = aws_security_group.fake_spine_alb_security_group.id
  type = "egress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = aws_security_group.fake_spine_security_group.id 
  description = "Allow ingress ${var.fake_spine_port} on application from LB"
}

# Allow incoming traffic from outbound to fake spine Load balancer

resource "aws_security_group_rule" "fake_spine_lb_sg_ingress_outbound_app_port" {
  security_group_id = aws_security_group.fake_spine_alb_security_group.id
  type = "ingress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = data.terraform_remote_state.mhs.outputs.outbound_sg_id
  description = "Allow ingress ${var.fake_spine_port} inbound requests from MHS outbound"
}

resource "aws_security_group_rule" "fake_spine_lb_sg_egress_outbound_app_port" {
  security_group_id = data.terraform_remote_state.mhs.outputs.outbound_sg_id
  type = "egress"
  from_port = var.fake_spine_port
  to_port = var.fake_spine_port
  protocol = "tcp"
  source_security_group_id = aws_security_group.fake_spine_alb_security_group.id
  description = "Allow egress ${var.fake_spine_port} inbound requests from MHS outbound"
}
