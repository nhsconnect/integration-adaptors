resource "aws_security_group_rule" "additional_container_from_incoming_cidr" {
  count = length(var.container_allowed_cidrs) > 0 ? 1 : 0
  type = "ingress"
  security_group_id =  aws_security_group.service_sg.id
  cidr_blocks = var.container_allowed_cidrs
  from_port = var.application_port
  to_port = var.application_port
  protocol = var.container_protocol
  description = "Allow additional CIDRs to  Container(s) in env: ${var.environment}"
}

resource "aws_security_group_rule" "additional_incoming_sg_to_container" {
  count = length(var.container_allowed_security_groups)
  type = "egress"
  source_security_group_id =  aws_security_group.service_sg.id
  security_group_id = var.container_allowed_security_groups[count.index]
  from_port = var.application_port
  to_port = var.application_port
  protocol = var.container_protocol
  description = "Allow additional SG: ${var.container_allowed_security_groups[count.index]} to Container(s) in env: ${var.environment}"
}

resource "aws_security_group_rule" "additional_container_from_incoming_sg" {
  count = length(var.container_allowed_security_groups)
  type = "ingress"
  security_group_id =  aws_security_group.service_sg.id
  source_security_group_id = var.container_allowed_security_groups[count.index]
  from_port = var.application_port
  to_port = var.application_port
  protocol = var.container_protocol
  description = "Allow from additional SG: ${var.container_allowed_security_groups[count.index]} to Load Balancer in env: ${var.environment}"
}
