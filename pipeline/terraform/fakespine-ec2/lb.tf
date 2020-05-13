resource "aws_lb" "fake_spine_load_balancer" {
  name = "${var.environment_id}-fake-spine-alb"
  internal = true
  load_balancer_type = "application"
  security_groups = [aws_security_group.fake_spine_alb_security_group.id]
  subnets =  data.terraform_remote_state.mhs.outputs.subnet_ids

  tags = {
    EnvironmentId = var.environment_id
  }
}

resource "aws_lb_listener" "fake_spine_listener" {
  load_balancer_arn = aws_lb.fake_spine_load_balancer.arn
  port = var.fake_spine_port
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.fake_spine_target_group.arn
  }
}

resource "aws_lb_target_group" "fake_spine_target_group" {
  name = "${var.environment_id}-fake-spine-tg"
  port = var.fake_spine_port
  protocol = "HTTP"
  vpc_id = data.terraform_remote_state.mhs.outputs.vpc_id

  health_check {
    enabled = true
    interval = 60
    path = "/healthcheck"
    protocol = "HTTP"
    timeout = 20
    healthy_threshold = 2
    unhealthy_threshold = 3
  }

  tags = {
    EnvironmentId = var.environment_id
  }
}

resource "aws_lb_target_group_attachment" "fake_spine_instance_attachment" {
  count = var.instance_count
  target_group_arn = aws_lb_target_group.fake_spine_target_group.arn
  target_id = aws_instance.fake_spine_instance[count.index].id
}