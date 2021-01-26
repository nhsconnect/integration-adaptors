locals {
    secret_variables = [
    {
      name = "MHS_SECRET_SPINE_ROUTE_LOOKUP_CA_CERTS"
      valueFrom = data.aws_secretsmanager_secret.spine_routelookup_ca_certs.arn
    },
    {
      name = "MHS_SECRET_PARTY_KEY"
      valueFrom = data.aws_secretsmanager_secret.mhs_party_key.arn
    },
    {
      name = "MHS_SECRET_CLIENT_CERT"
      valueFrom = data.aws_secretsmanager_secret.mhs_client_cert.arn
    },
    {
      name = "MHS_SECRET_CLIENT_KEY"
      valueFrom = data.aws_secretsmanager_secret.mhs_client_key.arn
    },
    {
      name = "MHS_SECRET_CA_CERTS"
      valueFrom = data.aws_secretsmanager_secret.mhs_ca_certs.arn
    },
    {
      name = "MHS_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "MHS_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    # {
    #   name = "MHS_MONGO_USERNAME"
    #   valueFrom = data.aws_secretsmanager_secret.docdb_master_username.arn
    # },
    # {
    #   name = "MHS_MONGO_PASSWORD"
    #   valueFrom = data.aws_secretsmanager_secret.docdb_master_password.arn
    # },
  ]
}
