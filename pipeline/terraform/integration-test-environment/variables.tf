variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "build_id" {
  type = string
  description = "ID used to identify the current build."
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
