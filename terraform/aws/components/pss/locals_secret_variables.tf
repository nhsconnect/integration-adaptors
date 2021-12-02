locals {
  secret_variables = [
    {
      name      = "pss_postgres_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_username.arn
    },
    {
      name      = "pss_postgres_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_password.arn
    },
    {
      name      = "PSS_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name      = "PSS_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
  ]
}