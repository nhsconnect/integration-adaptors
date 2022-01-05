/*
resource "aws_security_group_rule" "additional_outgoing_mhs_mock_to_jumpbox" {
  type = "egress"
  source_security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  security_group_id = aws_security_group.pss_external_access.id
  from_port = var.pss_mock_mhs_port
  to_port = var.pss_mock_mhs_port
  protocol = var.protocol
  description = "Allow additional SG: Jumpbox to testbox: ${var.environment}"
}

resource "aws_security_group_rule" "additional_outgoing_from_gpc_facade_to_jumpbox" {
  type = "egress"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  source_security_group_id = aws_security_group.pss_external_access.id
  from_port = var.pss_gpc_api_facade_container_port
  to_port = var.pss_gpc_api_facade_container_port
  protocol = var.protocol
  description = "Allow from additional SG: From testbox to Jumpbox in env: ${var.environment}"
}

resource "aws_security_group_rule" "additional_outgoing_from_gp2gp_translator_to_jumpbox" {
  type = "egress"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  source_security_group_id = aws_security_group.pss_external_access.id
  from_port = var.pss_gp2gp_translator_container_port
  to_port = var.pss_gp2gp_translator_container_port
  protocol = var.protocol
  description = "Allow from additional SG: From testbox to Jumpbox in env: ${var.environment}"
}
*/