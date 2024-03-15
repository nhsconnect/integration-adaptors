data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-nia-broker-password"
}

data "aws_secretsmanager_secret" "docdb_master_username" {
  name = "docdb-master-username"
}

data "aws_secretsmanager_secret" "docdb_master_password" {
  name = "docdb-master-password"
}

data "aws_secretsmanager_secret" "gp2gp_ssl_trust_store_password" {
  name = "nhais_${var.environment}_ssl_trust_store_password"
}

data "aws_secretsmanager_secret" "pds_key_id" {
  name = "pds-key-id"
}

data "aws_secretsmanager_secret" "pds_api_key" {
  name = "pds-api-key"
}

data "aws_secretsmanager_secret" "pds_private_key" {
  name = "pds-private-key"
}