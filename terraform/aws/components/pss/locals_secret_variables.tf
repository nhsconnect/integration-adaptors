locals {
  secret_variables = [
    {
      name      = "PSS_POSTGRES_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_username.arn
    },
    {
      name      = "PSS_POSTGRES_PASSWORD"
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
    {
      name = "PSS_DB_OWNER_NAME"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_username.arn
    },
    {
      name = "PSS_DB_OWNER_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_password.arn
    }
  ]
  secret_variables_pss_gp2gp_translator = [
    {
      name = "MHS_AMQP_USERNAME"
      valueFrom  = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "MHS_AMQP_PASSWORD"
      valueFrom  = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "GP2GP_USER_DB_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_password.arn
    }
  ]
  secret_variables_pss_gpc_api_facade = [
    {
      name = "GPC_USER_DB_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_password.arn
    }
  ]
}