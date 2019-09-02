resource "aws_lb" "outbound_alb" {
  internal = true
  load_balancer_type = "application"
  subnets = aws_subnet.mhs_subnet.*.id
  security_groups = [
    aws_security_group.alb_outbound_security_group.id
  ]

  tags = {
    Name = "${var.build_id}-mhs-outbound-alb"
    BuildId = var.build_id
  }
}

resource "aws_lb_target_group" "outbound_alb_target_group" {
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-outbound-alb-target-group"
    BuildId = var.build_id
  }
}

resource "aws_lb_listener" "outbound_alb_listener" {
  load_balancer_arn = aws_lb.outbound_alb.arn
  port = "80"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.outbound_alb_target_group.arn
  }
}

resource "aws_lb" "route_alb" {
  internal = true
  load_balancer_type = "application"
  subnets = aws_subnet.mhs_subnet.*.id
  security_groups = [
    aws_security_group.alb_route_security_group.id
  ]

  tags = {
    Name = "${var.build_id}-mhs-route-alb"
    BuildId = var.build_id
  }
}

resource "aws_lb_target_group" "route_alb_target_group" {
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-route-alb-target-group"
    BuildId = var.build_id
  }
}

resource "aws_lb_listener" "route_alb_listener" {
  load_balancer_arn = aws_lb.route_alb.arn
  port = "80"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.route_alb_target_group.arn
  }
}
