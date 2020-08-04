resource "aws_lb_target_group" "service_target_group" {
  count       = var.enable_load_balancing ? 1 : 0
  name        = "${replace(local.resource_prefix,"_","-")}-lb-tg"
  port        = var.container_port
  protocol    = var.protocol
  vpc_id      = var.vpc_id
  target_type = "ip"
  deregistration_delay = var.deregistration_delay

  health_check {
    enabled  = true
    interval = 30
    path     = var.healthcheck_path
    port     = local.healthcheck_port
    protocol = var.load_balancer_type == "application" ? var.protocol : null
    timeout  = var.load_balancer_type == "application" ? 20 : null
    matcher  = var.load_balancer_type == "application" ? "200-299" : null
    healthy_threshold   = var.load_balancer_type == "application" ? 3 : null
    unhealthy_threshold = var.load_balancer_type == "application" ? 3 : null
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-lb_tg"
  })

  depends_on = [aws_lb.service_load_balancer]
}