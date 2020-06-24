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
