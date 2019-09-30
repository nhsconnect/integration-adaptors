variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "build_id" {
  type = string
  description = "Build ID to identify the image in the ECR repo to use."
}

variable "environment_id" {
  type = string
  description = "An ID used to identify the environment being deployed by this configuration."
}

variable "cluster_id" {
  type = string
  description = "The ECS cluster to deploy to."
}

variable "task_execution_role" {
  type = string
  description = "ARN of the IAM role to run the task with."
}

variable "ecr_address" {
  type = string
  description = "Address of the ECR registry to get containers from."
}

variable "scr_log_level" {
  type = string
  description = "Log Level for the SCR Web Service"
}

variable "scr_service_port" {
  type = number
  description = "The port to be exposed for the scr web service"
}

variable "scr_mhs_address" {
  type = string
  description = "The address on the MHS for the SCR to forward messages to"
}

variable "scr_mhs_ca_certs_arn" {
  type = string
  description = "ARN of the secrets manager secret containing the CA certificates to be used to verify the certificate presented by the MHS. Required if your MHS is using certificates that are not signed by a legitimate CA."
  default = ""
}
