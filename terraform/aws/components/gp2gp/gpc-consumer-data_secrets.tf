data "aws_secretsmanager_secret" "gpc-consumer_mesh_mailbox_id" {
  name = "nhais_${var.environment}_mesh_mailbox_id"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_endpoint_private_key" {
  name = "nhais_${var.environment}_mesh_endpoint_private_key"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_shared_key" {
  name = "nhais_${var.environment}_mesh_shared_key"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_mailbox_password" {
  name = "nhais_${var.environment}_mesh_mailbox_password"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_endpoint_cert" {
  name = "nhais_${var.environment}_mesh_endpoint_cert"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_sub_ca" {
  name = "nhais_${var.environment}_mesh_sub_ca"
}

data "aws_secretsmanager_secret" "gpc-consumer_mesh_recipient_codes" {
  name = "nhais_${var.environment}_mesh_recipient_codes"
}

data "aws_secretsmanager_secret" "gpc-consumer_ssl_trust_store_password" {
  name = "nhais_${var.environment}_ssl_trust_store_password"
}

data "aws_secretsmanager_secret" "gpc-consumer_spine_client_cert" {
  name = var.secret_name_spine_client_cert
}

data "aws_secretsmanager_secret" "gpc-consumer_spine_client_key" {
  name = var.secret_name_spine_client_key
}

data "aws_secretsmanager_secret" "gpc-consumer_spine_root_ca_cert" {
  name = var.secret_name_spine_root_ca_cert
}

data "aws_secretsmanager_secret" "gpc-consumer_spine_sub_ca_cert" {
  name = var.secret_name_spine_sub_ca_cert
}

data "aws_secretsmanager_secret" "gpc-consumer_sds_apikey" {
  name = var.secret_name_sds_apikey
}