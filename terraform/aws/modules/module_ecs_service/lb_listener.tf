resource "aws_lb_listener" "service_listener" {
  count = var.enable_load_balancing ? 1 : 0
  load_balancer_arn = aws_lb.service_load_balancer[0].arn
  port              = var.application_port
  protocol          = var.protocol

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.service_target_group[0].arn
  }
}