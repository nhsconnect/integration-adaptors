resource "aws_security_group_rule" "allow_ingress_in_docdb" {
  type = "ingress"
  from_port = aws_docdb_cluster_instance.nhais_db_instance[0].port
  to_port = aws_docdb_cluster_instance.nhais_db_instance[0].port
  protocol = "tcp"
  security_group_id = aws_security_group.docdb_sg.id
  source_security_group_id = aws_security_group.docdb_access_sg.id
  description = "Allow incoming from application to document DB in env: ${var.environment}"
}

resource "aws_security_group_rule" "allow_egress_to_docdb" {
  type = "egress"
  from_port = aws_docdb_cluster_instance.nhais_db_instance[0].port
  to_port = aws_docdb_cluster_instance.nhais_db_instance[0].port
  protocol = "tcp"
  security_group_id = aws_security_group.docdb_access_sg.id
  source_security_group_id = aws_security_group.docdb_sg.id
  description = "Allow outgoing from application to document DB in env: ${var.environment}"
}
