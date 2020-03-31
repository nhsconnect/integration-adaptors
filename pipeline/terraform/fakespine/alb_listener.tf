# Listener for MHS outbound load balancer that forwards requests to the correct target group
resource "aws_lb_listener" "fake_spine_alb_listener" {
  load_balancer_arn = aws_lb.fake_spine_alb.arn
  port = 443
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn = var.fake_spine_alb_certificate_arn

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.fake_spine_alb_target_group.arn
  }
}
