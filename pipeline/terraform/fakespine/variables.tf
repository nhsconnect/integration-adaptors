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