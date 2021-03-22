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

# These are env specific, OpenTest certs and keys are different than HSCN ones.

data "aws_secretsmanager_secret" "mhs_party_key" {
  name = var.secret_name_mhs_party_key
}

data "aws_secretsmanager_secret" "mhs_client_cert" {
  name = var.secret_name_mhs_client_cert
}

data "aws_secretsmanager_secret" "mhs_client_key" {
  name = var.secret_name_mhs_client_key
}

data "aws_secretsmanager_secret" "mhs_ca_certs" {
  name = var.secret_name_mhs_ca_certs
}

data "aws_secretsmanager_secret" "spine_routelookup_ca_certs" {
  name = var.secret_name_mhs_spine_route_lookup_ca_certs
}
