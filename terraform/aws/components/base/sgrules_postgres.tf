/*
resource "aws_security_group_rule" "allow_ingress_in_postgres" {
  type = "ingress"
  from_port = aws_db_instance.base_postgres_db[0].port
  to_port = aws_db_instance.base_postgres_db[0].port
  protocol = "tcp"
  security_group_id = aws_security_group.postgres_sg.id
  source_security_group_id = aws_security_group.postgres_access_sg.id
  description = "Allow incoming from application to document DB in env: ${var.environment}"
}

resource "aws_security_group_rule" "allow_egress_to_postgres" {
  type = "egress"
  from_port = aws_db_instance.base_postgres_db[0].port
  to_port = aws_db_instance.base_postgres_db[0].port
  protocol = "tcp"
  security_group_id = aws_security_group.postgres_access_sg.id
  source_security_group_id = aws_security_group.postgres_sg.id
  description = "Allow outgoing from application to document DB in env: ${var.environment}"
} */
