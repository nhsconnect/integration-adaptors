data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-nia-broker-password"
}

data "aws_secretsmanager_secret" "postgres_master_username" {
  name = "postgres-master-username"
}

data "aws_secretsmanager_secret" "postgres_master_password" {
  name = "postgres-master-password"
}

data "aws_secretsmanager_secret" "postgres_psdbowner_username" {
  name = "postgres_psdbowner_username"
}

data "aws_secretsmanager_secret" "postgres_psdbowner_password" {
  name = "postgres_psdbowner_password"
}

data "aws_secretsmanager_secret" "postgres_gp2gp_translator_password" {
  name = "postgres_psdb_gp2gp_translator_user_password"
}

data "aws_secretsmanager_secret" "postgres_gpc_facade_password" {
  name = "postgres_psdb_gpc_facade_user_password"
}

data "aws_secretsmanager_secret_version" "postgres_psdbowner_username" {
  secret_id = data.aws_secretsmanager_secret.postgres_psdbowner_username.id
}

data "aws_secretsmanager_secret" "gpc-consumer_sds_apikey" {
  name = var.secret_name_sds_apikey
}
