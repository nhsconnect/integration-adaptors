data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-nia-broker-password"
}

data "aws_secretsmanager_secret" "docdb_master_username" {
  name = "docdb-master-username"
}

data "aws_secretsmanager_secret" "docdb_master_password" {
  name = "docdb-master-password"
}

data "aws_secretsmanager_secret" "lab-results_mesh_mailbox_id" {
  name = "lab-results_${var.environment}_mesh_mailbox_id"
}

data "aws_secretsmanager_secret" "lab-results_mesh_endpoint_private_key" {
  name = "lab-results_${var.environment}_mesh_endpoint_private_key"
}

data "aws_secretsmanager_secret" "lab-results_mesh_shared_key" {
  name = "lab-results_${var.environment}_mesh_shared_key"
}

data "aws_secretsmanager_secret" "lab-results_mesh_mailbox_password" {
  name = "lab-results_${var.environment}_mesh_mailbox_password"
}

data "aws_secretsmanager_secret" "lab-results_mesh_endpoint_cert" {
  name = "lab-results_${var.environment}_mesh_endpoint_cert"
}

data "aws_secretsmanager_secret" "lab-results_mesh_sub_ca" {
  name = "lab-results_${var.environment}_mesh_sub_ca"
}

data "aws_secretsmanager_secret" "lab-results_mesh_recipient_codes" {
  name = "lab-results_${var.environment}_mesh_recipient_codes"
}

data "aws_secretsmanager_secret" "lab-results_ssl_trust_store_password" {
  name = "lab-results_${var.environment}_ssl_trust_store_password"
}
