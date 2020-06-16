# vpc peering to the network where DLT is hosted

data "aws_vpc" "dlt_vpc" {
  count = var.enable_dlt ? 1 :0
  id = var.dlt_vpc_id
}

# DLT traffic - From the Distributed load tester to the load balancer

resource "aws_security_group_rule" "dlt_ingress_rule_to_loadbalancer" {
  count = var.enable_dlt ? 1 :0
  security_group_id = aws_security_group.service_lb_sg.id
  type = "ingress"
  from_port = var.application_port
  to_port = var.application_port
  protocol = var.container_protocol
  # Not making any assumptions here about the internal structure of the DLT VPC.
  # This can be changed and made more specific to lock this down more.
  cidr_blocks = [
    data.aws_vpc.dlt_vpc[0].cidr_block]
  description = "Allow inbound requests from DLT"
}

resource "aws_security_group_rule" "dlt_ingress_rule_to_service" {
  count = var.enable_dlt ? 1 :0
  security_group_id = aws_security_group.service_sg.id
  type = "ingress"
  from_port = var.application_port
  to_port = var.application_port
  protocol = var.container_protocol
  # Not making any assumptions here about the internal structure of the DLT VPC.
  # This can be changed and made more specific to lock this down more.
  cidr_blocks = [
    data.aws_vpc.dlt_vpc[0].cidr_block]
  description = "Allow inbound requests from DLT to service"
}
