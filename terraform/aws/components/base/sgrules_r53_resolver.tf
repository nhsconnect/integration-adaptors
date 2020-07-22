resource "aws_security_group_rule" "r53_resolver_53_from_core" {
  count = var.ptl_connected ? 1 : 0
  type = "ingress"
  from_port = 53
  to_port = 53
  protocol = "udp"
  source_security_group_id = aws_security_group.core_sg.id
  security_group_id = aws_security_group.r53_resolver_sg[0].id
  description = "Ingress from core network"
}

resource "aws_security_group_rule" "core_to_r53_resolver" {
  count = var.ptl_connected ? 1 : 0
  type = "egress"
  from_port = 53
  to_port = 53
  protocol = "udp"
  security_group_id = aws_security_group.core_sg.id
  source_security_group_id = aws_security_group.r53_resolver_sg[0].id
  description = "Egress to all DNS"
}

resource "aws_security_group_rule" "r53_resolver_53_to_everywhere" {
  count = var.ptl_connected ? 1 : 0
  type = "egress"
  from_port = 53
  to_port = 53
  protocol = "udp"
  security_group_id = aws_security_group.r53_resolver_sg[0].id
  cidr_blocks = ["0.0.0.0/0"]
  description = "Egress to all DNS"
}

resource "aws_security_group_rule" "ingress_nhs_dns" {
  count = var.ptl_connected ? 1 : 0
  type = "ingress"
  from_port = 53
  to_port = 53
  protocol = "udp"
  security_group_id = aws_security_group.r53_resolver_sg[0].id
  cidr_blocks = ["${var.ptl_dns_servers[0]}/32", "${var.ptl_dns_servers[1]}/32"]
  description = "Ingress from NHS DNS"
}
