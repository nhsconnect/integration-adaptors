data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-nia-broker-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-nia-broker-password"
}

# nginx secrets

data "aws_secretsmanager_secret" "nginx_server_certificate" {
  name = "nginx-111-server-public"
}

data "aws_secretsmanager_secret" "nginx_server_certificate_key" {
  name = "nginx-111-server-private"
}

data "aws_secretsmanager_secret" "nginx_ca_certificate" {
  name = "nginx-111-ca-cer"
}

data "aws_secretsmanager_secret" "nginx_client_certificate" {
  name = "nginx-111-client-public"
}
