locals {
    secret_variables = [
    {
      name = "LAB_RESULTS_AMQP_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.mq_username.arn
    },
    {
      name = "LAB_RESULTS_AMQP_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.mq_password.arn
    },
    {
      name = "LAB_RESULTS_MONGO_USERNAME"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_username.arn
    },
    {
      name = "LAB_RESULTS_MONGO_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.docdb_master_password.arn
    },
    {
      name = "LAB_RESULTS_MESH_MAILBOX_ID"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_mailbox_id.arn
    },
    {
      name = "LAB_RESULTS_MESH_MAILBOX_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_mailbox_password.arn
    },
    {
      name = "LAB_RESULTS_MESH_SHARED_KEY"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_shared_key.arn
    },
    {
      name = "LAB_RESULTS_MESH_ENDPOINT_CERT"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_endpoint_cert.arn
    },
    {
      name = "LAB_RESULTS_MESH_RECIPIENT_MAILBOX_ID_MAPPINGS"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_recipient_codes.arn
    },
    {
      name = "LAB_RESULTS_MESH_ENDPOINT_PRIVATE_KEY"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_endpoint_private_key.arn
    },
    {
      name = "LAB_RESULTS_MESH_SUB_CA"
      valueFrom = data.aws_secretsmanager_secret.lab-results_mesh_sub_ca.arn
    },
    {
      name = "LAB_RESULTS_SSL_TRUST_STORE_PASSWORD"
      valueFrom = data.aws_secretsmanager_secret.lab-results_ssl_trust_store_password.arn
    }
  ]
}
