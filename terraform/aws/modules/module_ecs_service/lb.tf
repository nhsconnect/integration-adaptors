resource "aws_lb" "service_load_balancer" {
  count = var.enable_load_balancing ? 1 :0
  name = "${replace(local.resource_prefix,"_","-")}-lb"
  internal = true
  load_balancer_type = var.load_balancer_type
  security_groups = [aws_security_group.service_lb_sg.id]
  subnets = var.subnet_ids

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-lb"
  })
}