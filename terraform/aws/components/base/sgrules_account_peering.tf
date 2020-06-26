# Allow account's jumpbox to connect to docdb
resource "aws_security_group_rule" "allow_docdb_from_jumpbox" {
  type = "ingress"
  description = "Allow incoming from jumpbox to documentDB in env ${var.environment}"
  from_port = aws_docdb_cluster_instance.base_db_instance[0].port
  to_port = aws_docdb_cluster_instance.base_db_instance[0].port
  protocol = "tcp"
  security_group_id = aws_security_group.docdb_sg.id
  source_security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  depends_on = [aws_vpc_peering_connection.account_peering]
}

resource "aws_security_group_rule" "allow_jumpbox_to_docdb" {
  type = "egress"
  description = "Allow outgoing from jumpbox to documentDB in env ${var.environment}"
  from_port = aws_docdb_cluster_instance.base_db_instance[0].port
  to_port = aws_docdb_cluster_instance.base_db_instance[0].port
  protocol = "tcp"
  security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  source_security_group_id = aws_security_group.docdb_sg.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}
