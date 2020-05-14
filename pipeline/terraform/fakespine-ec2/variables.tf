variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "environment_id" {
  type = string
  description = "An ID used to identify the environment being deployed by this configuration. As this is used as a prefix for the names of most resources this should be kept to 20 characters or less."
}

variable "ecr_address" {
  type = string
  description = "Address of the ECR registry to get containers from."
}

variable "build_id" {
  type = string
  description = "ID used to identify the current build."
}

variable "execution_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to pull from ECR and put logs in Cloudwatch."
}

variable "mhs_state_bucket" {
  type = string
  description = "Name of bucket with MHS component state"
}

variable "fake_spine_service_minimum_instance_count" {
  type = number
  description = "The minimum number of instances of fake-spine to run. This will be the number of instances deployed initially."
  default = 3
}

variable "fake_spine_service_maximum_instance_count" {
  type = number
  description = "The maximum number of instances of fake-spine to run."
  default = 9
}

variable "fake_spine_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an fake_spine service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "task_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to use other AWS services."
}

variable "fake_spine_alb_certificate_arn" {
  type = string
  description = "ARN of the TLS certificate that the fake-spine load balancer should present. This can be a certificate stored in IAM or ACM."
}

variable "task_scaling_role_arn" {
  type = string
  description = "ARN of the IAM role for ECS to use when auto-scaling services"
}

variable "inbound_server_base_url" {
  type = string
  description = "URL of the inbound server"
  default = ""
}

variable "outbound_delay_ms" {
  type = string
  description = "Delay in miliseconds for outgoing communication"
}

variable "inbound_delay_ms" {
  type = string
  description = "Delay in miliseconds for incoming communication"
}

variable "fake_spine_private_key" {
  type = string
  description = "Private key for certificate used by fake spine"
}

variable "fake_spine_certificate" {
  type = string
  description = "Certificate for fake spine"
}

variable "fake_spine_ca_store" {
  type = string
  description = "CA store for fake spine"
}

variable "party_key_arn" {
  type = string
  description = "Secret key for communication with MHS"
}

variable "fake_spine_outbound_ssl" {
  type = string
  description ="Should the SSL on fake spine service be enabled"
}

variable "fake_spine_port" {
  type = string
  description = "Port on which tne service will listen to connections"
}

variable "git_branch_name" {
  type = string
  description = "Branch to clone inside the EC2 instance"
}

variable "git_repo_url" {
  type = string
  description = "Repository to clone inside the EC2 instance"
}

variable "mhs_inbound_port" {
  type = number
  description = "Port in which mhs inbound runs"
  default = 443
}

variable "fake_spine_proxy_validate_cert" {
  type = string
  description = "Validate certificate for proxy"
}

variable "instance_count" {
  type = number
  default = 4
  description = "How many fakespine intances do we need"
}

variable "mhs_log_level" {
  type = string
  default = "INFO"
  description = "Log level for application"
}
