resource "aws_security_group_rule" "additional_incoming_jumpbox_to_testbox" {
  type = "egress"
  source_security_group_id =  aws_security_group.pss_testbox_sg.id
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  from_port = var.pss_service_application_port
  to_port = var.pss_service_application_port
  protocol = var.protocol
  description = "Allow additional SG: Jumpbox to testbox: ${var.environment}"
}

resource "aws_security_group_rule" "additional_outgoing_from_testbox_to_jumpbox" {
  type = "ingress"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  source_security_group_id = aws_security_group.pss_testbox_sg.id
  from_port = var.pss_service_application_port
  to_port = var.pss_service_application_port
  protocol = var.protocol
  description = "Allow from additional SG: From testbox to Jumpbox in env: ${var.environment}"
}

/*resource "aws_security_group_rule" "pss_testbox_80_internet" {
  description = "Allow testbox to connect to internet on 80"
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  security_group_id = aws_security_group.pss_testbox_sg.id
  cidr_blocks = [data.terraform_remote_state.base.outputs.pss_cidr]
}

resource "aws_security_group_rule" "pss_testbox_443_internet" {
  description = "Allow testbox to connect to internet on 443"
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  security_group_id = aws_security_group.pss_testbox_sg.id
  cidr_blocks = [data.terraform_remote_state.base.outputs.pss_cidr]
}*/