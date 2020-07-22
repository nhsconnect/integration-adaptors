resource "aws_security_group_rule" "jumpbox_22_from_cidrs" {
  count = length(var.jumpbox_allowed_ssh) > 0 ? 1 : 0
  description = "Allow SSH connection from listed CIDRS"
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  security_group_id = aws_security_group.jumpbox_sg.id
  cidr_blocks = var.jumpbox_allowed_ssh
}

resource "aws_security_group_rule" "jumpbox_22_internet" {
  description = "Allow jumpbox to connect everywhere on 22"
  type = "egress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  security_group_id = aws_security_group.jumpbox_sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "jumpbox_80_internet" {
  description = "Allow jumpbox to connect to internet on 80"
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  security_group_id = aws_security_group.jumpbox_sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "jumpbox_443_internet" {
  description = "Allow jumpbox to connect to internet on 443"
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  security_group_id = aws_security_group.jumpbox_sg.id
  cidr_blocks = ["0.0.0.0/0"]
}
