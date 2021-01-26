resource "aws_security_group_rule" "allow_ingress_in_ec" {
  type = "ingress"
  from_port = aws_elasticache_replication_group.elasticache_replication_group.port
  to_port = aws_elasticache_replication_group.elasticache_replication_group.port
  protocol = "tcp"
  security_group_id = aws_security_group.elasticache_sg.id
  source_security_group_id = aws_security_group.core_sg.id
  description = "Allow incoming from application to Redis in env: ${var.environment}"
}

resource "aws_security_group_rule" "allow_egress_to_ec" {
  type = "egress"
  from_port = aws_elasticache_replication_group.elasticache_replication_group.port
  to_port = aws_elasticache_replication_group.elasticache_replication_group.port
  protocol = "tcp"
  security_group_id = aws_security_group.core_sg.id
  source_security_group_id = aws_security_group.elasticache_sg.id
  description = "Allow outgoing from application to Redis in env: ${var.environment}"
}
