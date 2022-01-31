resource "aws_db_instance" "base_postgres_db" {
  count                           = var.create_postgres_db ? 1 : 0
  allocated_storage               = "20"
  identifier                      = "${replace(local.resource_prefix,"_","-")}-psdb-instance"
  engine                          = "postgres"
  instance_class                  = var.postgres_instance_class
  username                        = var.postgres_master_user
  password                        = var.postgres_master_password
  backup_retention_period         = var.postgres_retention_period
  skip_final_snapshot             = true
  port                            = var.postgres_port
  db_subnet_group_name            = aws_db_subnet_group.base_postgres_subnet_group.name
  parameter_group_name            = aws_db_parameter_group.postgres_base_parameter.name
  vpc_security_group_ids          = [ aws_security_group.postgres_sg.id ]
  enabled_cloudwatch_logs_exports = ["postgresql"]
  storage_encrypted               = var.postgres_storage_encrypted
  kms_key_id                      = var.postgres_kms_key_id
  availability_zone               = local.availability_zones[ count.index ]
  apply_immediately               = true

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-psdb-instance"
    EnableScheduler = var.enable_postgres_scheduler
  })
}
