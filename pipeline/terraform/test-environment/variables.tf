variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}
variable "profile" {
  type = string
  default = "default"
  description = "The profile to use for the aws cli."
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
variable "queue_security_group_id" {
  type = string
  description = "The security group to use for the queues"
}
variable "environment" {
  type = string
  description = "A name for the environment to be used."
  default = "test"
}
variable "queue_user" {
  type = string
  description = "The username for the default user to use."
}
variable "queue_pass" {
  type = string
  description = "The password for the default user to use."
}