resource "aws_security_group_rule" "nhais_to_fakemesh"{
  type = "egress"
  from_port = 8829
  to_port = 8829
  protocol = "TCP"
  security_group_id = data.terraform_remote_state.nhais.outputs.nhais_external_access_sg_id
  cidr_blocks = [
    data.terraform_remote_state.base.outputs.nhais_cidr
  ]
}

resource "aws_security_group_rule" "jumpbox_to_fakemesh"{
  type = "egress"
  from_port = 8829
  to_port = 8829
  protocol = "TCP"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  cidr_blocks = [
    data.terraform_remote_state.base.outputs.nhais_cidr
  ]
}
