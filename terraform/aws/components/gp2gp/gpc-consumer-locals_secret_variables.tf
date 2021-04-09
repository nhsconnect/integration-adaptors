locals {
    gpcc_secret_variables = [
  ]
}

locals {
  gpcc_spine_secrets = [
    {
      name = "GPC_CONSUMER_SPINE_CLIENT_CERT"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_spine_client_cert.arn
    },
    {
      name = "GPC_CONSUMER_SPINE_CLIENT_KEY"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_spine_client_key.arn
    },
    {
      name = "GPC_CONSUMER_SPINE_ROOT_CA_CERT"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_spine_root_ca_cert.arn
    },
    {
      name = "GPC_CONSUMER_SPINE_SUB_CA_CERT"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_spine_sub_ca_cert.arn
    },
    {
      name = "GPC_CONSUMER_SDS_APIKEY"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_sds_apikey.arn
    }
  ]
}