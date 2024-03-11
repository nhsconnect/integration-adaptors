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
    },
    {
      name      = "GP2GP_SSL_TRUST_STORE_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.gp2gp_ssl_trust_store_password.arn
    }
  ]

  wiremock_secret_variables = [
    {
      name      = "PDS_KEY_ID"
      valueFrom = data.aws_secretsmanager_secret.pds_key_id.arn
    },
    {
      name      = "PDS_API_KEY"
      valueFrom = data.aws_secretsmanager_secret.pds_api_key.arn
    },
    {
      name      = "PDS_PRIVATE_KEY"
      valueFrom = data.aws_secretsmanager_secret.pds_private_key.arn
    }
  ]
}
