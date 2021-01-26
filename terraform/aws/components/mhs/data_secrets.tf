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

data "aws_secretsmanager_secret" "mhs_party_key" {
  name = "opentest-party-key"
}

data "aws_secretsmanager_secret" "mhs_client_cert" {
  name = "opentest-client-certificate"
}

data "aws_secretsmanager_secret" "mhs_client_key" {
  name = "opentest-client-key"
}

data "aws_secretsmanager_secret" "mhs_ca_certs" {
  name = "opentest-ca-certs"
}

data "aws_secretsmanager_secret" "spine_routelookup_ca_certs" {
  name = "build-outbound-route-connection-cacerts"
}
