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

# variable "nhais_ecr_repository_name" {
#   type = string
#   description = "Name for NHAIS ECR repository"
# }

# variable "ecr_repository_name_111" {
#   type = string
#   description = "Name for 111 ECR repository"
# }

variable "ecr_repositories" {
  type = list(object({
    name=string,
    scan=bool,
    expire_PR_after=number,
    prefix_to_keep=string,
    number_to_keep=number
  }))
  description = "List of ECR repositories to create"
  default = []
}

variable "account_cidr_block" {
  type = string
  description = "CIDR for vpc in account component"
}

variable "jumpbox_allowed_ssh" {
  type = list(string)
  description = "List of CIDR that are allowed to SSH to jumpbox"
  default = []
}