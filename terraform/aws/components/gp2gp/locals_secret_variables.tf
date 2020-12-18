locals {
  secret_variables = [
    {
      name      = "GP2GP_MONGO_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_username.arn
    },
    {
      name      = "GP2GP_MONGO_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_password.arn
    },
    {
      name      = "GP2GP_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name      = "GP2GP_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    }
  ]
}
