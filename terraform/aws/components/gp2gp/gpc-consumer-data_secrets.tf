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