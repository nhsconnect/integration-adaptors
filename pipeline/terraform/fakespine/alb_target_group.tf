# Target group for the application load balancer for MHS outbound
# The MHS outbound ECS service registers it's tasks here.
resource "aws_lb_target_group" "fake_spine_alb_target_group" {
  port = 443
  protocol = "HTTPS"
  target_type = "ip"
  vpc_id = data.terraform_remote_state.mhs.outputs.vpc_id
  name = "${var.environment_id}-fake-spine-alb-tg"

  health_check {
    path = "/healthcheck"
    matcher = "200"
    port = 80
  }

  tags = {
    Name = "${var.environment_id}-fake-spine-alb-tg"
    EnvironmentId = var.environment_id
  }
}
