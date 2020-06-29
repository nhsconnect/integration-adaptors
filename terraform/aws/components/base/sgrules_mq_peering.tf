resource "aws_security_group_rule" "base_core_to_mq" {
  security_group_id = aws_security_group.core_sg.id
  type = "egress"
  from_port = 5671
  to_port = 5671
  protocol = "tcp"
  source_security_group_id = var.mq_sg_id
  description = "Allow requests to Amazon MQ inbound queue"
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

resource "aws_security_group_rule" "mq_from_base_core" {
  source_security_group_id = aws_security_group.core_sg.id
  type = "ingress"
  from_port = 5671
  to_port = 5671
  protocol = "tcp"
  security_group_id = var.mq_sg_id
  description = "Allow AMQP from ${var.environment} env"
  depends_on = [aws_vpc_peering_connection.mq_peering]
}
