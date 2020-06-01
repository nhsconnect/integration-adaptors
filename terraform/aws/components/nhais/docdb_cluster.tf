resource "aws_docdb_cluster" "nhais_db_cluster" {
  cluster_identifier = "${replace(local.resource_prefix,"_","-")}-dbcluster"
  engine = "docdb"
  master_username                 = var.docdb_master_user
  master_password                 = var.docdb_master_password
  backup_retention_period         = var.docdb_retention_period
  skip_final_snapshot             = true
  db_subnet_group_name            = aws_docdb_subnet_group.nhais_db_subnet_group.name
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.nhais_db_parameters.name
  vpc_security_group_ids          = [ aws_security_group.docdb_sg.id ]
  enabled_cloudwatch_logs_exports = ["audit"]

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-dbcluster"
  })
}
