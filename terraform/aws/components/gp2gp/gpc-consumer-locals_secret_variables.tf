locals {
    gpcc_secret_variables = [
    {
      name = "GPC_CONSUMER_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "GPC_CONSUMER_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "GPC_CONSUMER_MONGO_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_username.arn
    },
    {
      name = "GPC_CONSUMER_MONGO_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_password.arn
    },
    {
      name = "GPC_CONSUMER_MESH_MAILBOX_ID"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_mailbox_id.arn
    },
    {
      name = "GPC_CONSUMER_MESH_MAILBOX_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_mailbox_password.arn
    },
    {
      name = "GPC_CONSUMER_MESH_SHARED_KEY"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_shared_key.arn
    },
    {
      name = "GPC_CONSUMER_MESH_ENDPOINT_CERT"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_endpoint_cert.arn
    },
    {
      name = "GPC_CONSUMER_MESH_RECIPIENT_MAILBOX_ID_MAPPINGS"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_recipient_codes.arn
    },
    {
      name = "GPC_CONSUMER_MESH_ENDPOINT_PRIVATE_KEY"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_endpoint_private_key.arn
    },
    {
      name = "GPC_CONSUMER_MESH_SUB_CA"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_mesh_sub_ca.arn
    },
    {
      name = "GPC_CONSUMER_SSL_TRUST_STORE_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.gpc-consumer_ssl_trust_store_password.arn
    },
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