resource "aws_security_group_rule" "pss_to_fakemesh"{
  type = "egress"
  from_port = 8829
  to_port = 8829
  protocol = "TCP"
  security_group_id = aws_security_group.pss_external_access.id
  cidr_blocks = [
    data.terraform_remote_state.base.outputs.nhais_cidr
  ]
}
