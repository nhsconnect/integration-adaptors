variable "project" {
  type = string
  description = "Name of the project where this code is used"
}

variable "environment" {
  type = string
  description = "Name of the environment"
}

variable "component" {
  type = string
  description = "Name of the component"
  default = "account"
}

variable "region" {
  type = string
  description = "Region where the resources will be created"
}

variable "tf_state_bucket" {
  type = string
  description = "Name of S3 bucket with TF state of components"
}

variable "nhais_ecr_repository_name" {
  type = string
  description = "Name for NHAIS ECR repository"
}