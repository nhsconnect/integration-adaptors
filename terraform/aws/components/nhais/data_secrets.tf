data "aws_secretsmanager_secret" "mq_username" {
  name = "amazon-mq-inbound-queue-username"
}

data "aws_secretsmanager_secret" "mq_password" {
  name = "amazon-mq-inbound-queue-password"
}