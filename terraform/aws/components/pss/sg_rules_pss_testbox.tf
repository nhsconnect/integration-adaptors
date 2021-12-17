resource "aws_security_group_rule" "connect_to_testbox" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [data.terraform_remote_state.account.outputs.jumpbox_sg_id]
  security_group_id = aws_security_group.pss_testbox_sg.id
}

resource "aws_security_group_rule" "connect_to_jumpbox" {
  type              = "egress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [data.terraform_remote_state.base.outputs.pss_cidr]
  security_group_id = aws_security_group.pss_testbox_sg.id
}

resource "aws_security_group_rule" "pss_testbox_80_internet" {
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
}

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