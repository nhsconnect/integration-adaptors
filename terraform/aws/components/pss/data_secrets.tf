data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-nia-broker-password"
}

data "aws_secretsmanager_secret" "postgres_master_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "postgres_master_password" {
  name = "postgres-master-password"
}