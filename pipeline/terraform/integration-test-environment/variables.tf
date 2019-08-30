variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "build_id" {
  type = string
  description = "ID used to identify the current build."
}

variable "mhs_outbound_service_instance_count" {
  type = number
  description = "The desired number of instances of MHS outbound to run."
}

variable "mhs_inbound_service_instance_count" {
  type = number
  description = "The desired number of instances of MHS inbound to run."
}

variable "task_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to use other AWS services."
}

variable "execution_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to pull from ECR and put logs in Cloudwatch."
}

variable "ecr_address" {
  type = string
  description = "Address of the ECR registry to get containers from."
}

variable "mhs_log_level" {
  type = string
  description = "Log level for the MHS application."
}

variable "mhs_state_table_name" {
  type = string
  description = "Name of the DynamoDB state table used by the MHS application."
}

variable "mhs_sync_async_table_name" {
  type = string
  description = "Name of the DynamoDB sync-async table used by the MHS application."
}

variable "inbound_queue_host" {
  type = string
  description = "URL of the Amazon MQ AMQP inbound queue to connect to."
}

variable "inbound_queue_username_arn" {
  type = string
  description = "ARN of the secrets manager secret of the username to use when connecting to the inbound queue."
}

variable "inbound_queue_password_arn" {
  type = string
  description = "ARN of the secrets manager secret of the password to use when connecting to the inbound queue."
}

variable "party_key_arn" {
  type = string
  description = "ARN of the secrets manager secret of the party key associated with the MHS."
}

variable "client_cert_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint certificate."
}

variable "client_key_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint private key."
}

variable "ca_certs_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint certificate, endpoint issuing subCA certificate, root CA Certificate (all in that order)."
}
