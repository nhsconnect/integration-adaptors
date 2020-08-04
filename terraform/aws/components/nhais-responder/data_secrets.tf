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

data "aws_secretsmanager_secret" "nhais_mesh_mailbox_id" {
  name = "nhais_mesh_mailbox_id"
}

data "aws_secretsmanager_secret" "nhais_mesh_endpoint_private_key" {
  name = "nhais_mesh_endpoint_private_key"
}

data "aws_secretsmanager_secret" "nhais_mesh_shared_key" {
  name = "nhais_mesh_shared_key"
}

data "aws_secretsmanager_secret" "nhais_mesh_mailbox_password" {
  name = "nhais_mesh_mailbox_password"
}

data "aws_secretsmanager_secret" "nhais_mesh_endpoint_cert" {
  name = "nhais_mesh_endpoint_cert"
}

data "aws_secretsmanager_secret" "nhais_mesh_recipient_codes" {
  name = "nhais_mesh_recipient_codes"
}
