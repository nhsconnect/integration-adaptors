resource "aws_security_group_rule" "additional_incoming_jumpbox_to_testbox" {
  security_group_id = aws_security_group.pss_testbox_sg.id
  type = "ingress"
  protocol = var.protocol
  from_port = 22
  to_port = 22
  source_security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  description = "Allow from Jumpbox to PSS Testbox in env: ${var.environment}"
}


#################################
# PSS Testbox Access To Internet
#################################

resource "aws_security_group_rule" "pss_testbox_80_internet" {
  security_group_id = aws_security_group.pss_testbox_sg.id
  type = "egress"
  protocol = "tcp"
  from_port = 80
  to_port = 80
  cidr_blocks = ["0.0.0.0/0"]
  description = "Allow pss testbox to connect to internet on 80 in env: ${var.environment}"
}

resource "aws_security_group_rule" "pss_testbox_443_internet" {
  security_group_id = aws_security_group.pss_testbox_sg.id
  type = "egress"
  protocol = "tcp"
  from_port = 443
  to_port = 443
  cidr_blocks = ["0.0.0.0/0"]
  description = "Allow pss testbox to connect to internet on 443 in env: ${var.environment}"
}

/*
#####################################
# PSS Testbox Access To PostgreSQL DB
#####################################

resource "aws_security_group_rule" "allow_testbox_to_postgres" {
  security_group_id = aws_security_group.pss_testbox_sg.id
  type = "egress"
  protocol = "tcp"
  from_port = data.terraform_remote_state.base.outputs.postgres_instance_port
  to_port = data.terraform_remote_state.base.outputs.postgres_instance_port
  source_security_group_id = data.terraform_remote_state.base.outputs.postgres_access_sg_id
  description = "Allow outgoing from pss testbox to PostgreSQL DB in env: ${var.environment}"
}

resource "aws_security_group_rule" "allow_postgres_from_testbox" {
  security_group_id = data.terraform_remote_state.base.outputs.postgres_access_sg_id
  type = "ingress"
  protocol = "tcp"
  from_port = data.terraform_remote_state.base.outputs.postgres_instance_port
  to_port = data.terraform_remote_state.base.outputs.postgres_instance_port
  source_security_group_id = aws_security_group.pss_testbox_sg.id
  description = "Allow incoming from pss testbox to PostgreSQL DB in env: ${var.environment}"
}

resource "aws_security_group_rule" "additional_incoming_jumpbox_to_testbox" {
  type = "egress"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  source_security_group_id =  aws_security_group.pss_testbox_sg.id
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
*/
