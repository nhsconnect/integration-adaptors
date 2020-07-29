resource "aws_security_group" "nhais_external_access" {
  name = "${local.resource_prefix}-nhais_access_sg"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nhais_access_sg"
  })
  description = "SG for additional nhais access in env: ${var.environment}"
}

resource "aws_security_group_rule" "nhais_to_fakemesh"{
  type = "egress"
  from_port = 8829
  to_port = 8829
  protocol = "TCP"
  security_group_id = aws_security_group.nhais_external_access.id
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
