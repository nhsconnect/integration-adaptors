resource "aws_security_group_rule" "from_load_balancer_to_service" {
  type = "egress"
  from_port = var.container_port
  to_port = var.container_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_lb_sg.id
  source_security_group_id = aws_security_group.service_sg.id
  description = "Allow application connection to Service from Load Balancer"
}

resource "aws_security_group_rule" "to_service_from_load_balancer" {
  type = "ingress"
  from_port = var.container_port
  to_port = var.container_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_sg.id
  source_security_group_id = aws_security_group.service_lb_sg.id
  description = "Allow application connection from Load Balancer to service"
}

resource "aws_security_group_rule" "to_service_from_network_load_balancer" {
  count = local.network_lb
  type = "ingress"
  from_port = var.container_port
  to_port = var.container_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_sg.id
  cidr_blocks = [
    data.aws_subnet.lb_subnets[0].cidr_block,
    data.aws_subnet.lb_subnets[1].cidr_block,
    data.aws_subnet.lb_subnets[2].cidr_block
  ]
  description = "Allow application from LB subnets"
}

# Healtheck rules - apply only if healthcheck port is different than main port

resource "aws_security_group_rule" "healthcheck_from_load_balancer_to_service" {
  count = var.container_port == local.healthcheck_port ? 0 : 1
  type = "egress"
  from_port = local.healthcheck_port
  to_port = local.healthcheck_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_lb_sg.id
  source_security_group_id = aws_security_group.service_sg.id
  description = "Allow healthcheck connection from Load Balancer to Service"
}

resource "aws_security_group_rule" "healthcheck_to_service_from_load_balancer" {
  count = var.container_port == local.healthcheck_port ? 0 : 1
  type = "ingress"
  from_port = local.healthcheck_port
  to_port = local.healthcheck_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_sg.id
  source_security_group_id = aws_security_group.service_lb_sg.id
  description = "Allow healthcheck connection to Service from Load Balancer"
}

resource "aws_security_group_rule" "healthcheck_to_service_from_network_load_balancer" {
  count = var.container_port == local.healthcheck_port ? 0 : local.network_lb
  type = "ingress"
  from_port = local.healthcheck_port
  to_port = local.healthcheck_port
  protocol = var.container_protocol
  security_group_id = aws_security_group.service_sg.id
  cidr_blocks = [
    data.aws_subnet.lb_subnets[0].cidr_block,
    data.aws_subnet.lb_subnets[1].cidr_block,
    data.aws_subnet.lb_subnets[2].cidr_block
  ]
  description = "Allow healthchecks from LB subnets"
}

data "aws_subnet" "lb_subnets" {
  count = length(var.lb_subnet_ids)
  id = var.lb_subnet_ids[count.index]
}