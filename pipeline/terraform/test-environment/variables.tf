variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "cluster_id" {
  type = string
  description = "The ECS cluster to deploy to."
}
variable "task_execution_role" {
  type = string
  description = "ARN of the IAM role to run the task with."
}
variable "build_id" {
  type = string
  description = "Build ID to identify the image in the ECR repo to use."
}
variable "ecr_address" {
  type = string
  description = "Address of the ECR repository to get the container from."
}
variable "mhs_log_level" {
  type = string
  description = "Log level for the MHS application."
}
variable "mhs_state_table_name" {
  type = string
  description = "Name of the DynamoDB state table used by the MHS application."
}
variable "scr_log_level" {
  type = string
  description = "Log Level for the SCR Web Service"
}
variable "scr_ecr_address" {
  type = string
  description = "The address of the ECR repository containing the scr-service containers"
}
variable "scr_service_port" {
  type = number
  description = "The port to be exposed for the scr web service"
}
variable "mhs_inbound_queue_host" {
  type = string
  description = "The address of the async inbound queue"
}
variable "mhs_inbound_queue_username" {
  type = string
  description = "The username of the async inbound queue"
}
variable "mhs_inbound_queue_password" {
  type = string
  description = "The password for the async inbound queue"
}
variable "mhs_sync_async_state_table_name" {
  type = string
  description = "The name of the sync async store table"
}
