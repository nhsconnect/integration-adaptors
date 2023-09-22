locals {
  secret_variables = [
    {
      name      = "PS_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name      = "PS_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name      = "PS_POSTGRES_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_username.arn
    },
    {
      name      = "PS_POSTGRES_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_master_password.arn
    },
    {
      name = "PS_DB_OWNER_NAME"
      valueFrom = data.aws_secretsmanager_secret.postgres_psdbowner_username.arn
    },
    {
      name = "PS_DB_OWNER_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.postgres_psdbowner_password.arn
    }
  ]
  pss_gp2gp_translator_secret_variables = [
    {
      name = "GP2GP_TRANSLATOR_USER_DB_PASSWORD"
      valueFrom  = data.aws_secretsmanager_secret.postgres_gp2gp_translator_password.arn
    },
    {
      name = "MHS_AMQP_USERNAME"
      valueFrom  = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "MHS_AMQP_PASSWORD"
      valueFrom  = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "GP2GP_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "GP2GP_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "SDS_API_KEY"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_sds_apikey.arn
    }
  ]
  pss_gpc_api_facade_secret_variables = [
    {
      name = "GPC_FACADE_USER_DB_PASSWORD"
      valueFrom  = data.aws_secretsmanager_secret.postgres_gpc_facade_password.arn
    }
  ]
}