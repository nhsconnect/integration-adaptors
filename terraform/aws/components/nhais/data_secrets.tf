data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-inbound-queue-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-inbound-queue-password"
}

data "aws_secretsmanager_secret" "docdb_master_username" {
  name = "docdb_master_username"
}

data "aws_secretsmanager_secret" "docdb_master_password" {
  name = "docdb_master_password"
}