resource "aws_security_group_rule" "connect_to_mhs_mock" {
  description = "Allow testbox to connect to internet on 8080"
  type = "egress"
  from_port = 8080
  to_port = 8080
  protocol = "tcp"
  security_group_id = aws_security_group.pss_testbox_sg.id
  cidr_blocks = [data.terraform_remote_state.base.outputs.pss_cidr]
}

resource "aws_security_group_rule" "connect_to_gp2gp_tl" {
  description = "Allow testbox to connect to internet on 8085"
  type = "egress"
  from_port = 8085
  to_port = 8085
  protocol = "tcp"
  security_group_id = aws_security_group.pss_testbox_sg.id
  cidr_blocks = [data.terraform_remote_state.base.outputs.pss_cidr]
}

resource "aws_security_group_rule" "connect_to_gpc_facade" {
  description = "Allow testbox to connect to internet on 8081"
  type = "egress"
  from_port = 8081
  to_port = 8081
  protocol = "tcp"
  security_group_id = aws_security_group.pss_testbox_sg.id
  cidr_blocks = [data.terraform_remote_state.base.outputs.pss_cidr]
}