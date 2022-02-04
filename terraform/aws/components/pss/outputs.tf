# place for outputs from component


output "PS_DB_URL" {
  value = "jdbc:postgresql://${data.terraform_remote_state.base.outputs.postgres_instance_endpoint}"
}

output "PS_DBOWNER_USERNAME" {
  value = data.aws_secretsmanager_secret_version.postgres_psdbowner_username.secret_string
}
