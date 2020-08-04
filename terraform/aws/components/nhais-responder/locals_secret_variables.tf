locals {
    secret_variables = [
    {
      name = "NHAIS_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "NHAIS_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "NHAIS_MONGO_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_username.arn
    },
    {
      name = "NHAIS_MONGO_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_password.arn
    },
    {
      name = "NHAIS_MESH_MAILBOX_ID"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_mailbox_id.arn
    },
    {
      name = "NHAIS_MESH_MAILBOX_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_mailbox_password.arn
    },
    {
      name = "NHAIS_MESH_SHARED_KEY"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_shared_key.arn
    },
    {
      name = "NHAIS_MESH_ENDPOINT_CERT"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_endpoint_cert.arn
    },
    {
      name = "NHAIS_MESH_RECIPIENT_CODES"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_recipient_codes.arn
    },
    {
      name = "NHAIS_MESH_ENDPOINT_PRIVATE_KEY"
      valueFrom = data.aws_secretsmanager_secret.nhais_mesh_endpoint_private_key.arn
    }
  ]
}
