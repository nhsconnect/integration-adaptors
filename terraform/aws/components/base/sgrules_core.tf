resource "aws_security_group_rule" "core_to_internet_443" {
  count = var.enable_internet_access ? 1 : 0
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  security_group_id = aws_security_group.core_sg.id
  cidr_blocks = ["0.0.0.0/0"]
  description = "Allow outgoing internet traffic on 443 in env: ${var.environment}"
}
