resource "aws_security_group" "service_sg" { 
  name = "${local.resource_prefix}-sg"
  vpc_id = var.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-sg"
  })
  description = "SG for app: ${var.component} in env: ${var.environment}"

}

resource "aws_security_group" "service_lb_sg" {
  name = "${local.resource_prefix}-lb_sg"
  vpc_id = var.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-lb_sg"
  })
  description = "SG for Load Balancer for app: ${var.component} in env: ${var.environment}"
}
