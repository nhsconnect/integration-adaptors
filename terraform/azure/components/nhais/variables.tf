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
  default = "nhais"
}

variable location {
  description = "Azure Location (Region)"
  type = string
}

variable state_bucket_resource_group {
  description = "Resource group which contains bucket with TF state file"
  type = string
}

variable state_bucket_storage_account {
  description = "Name of storage account with TF state bucket"
  type = string
}

variable state_bucket_name {
  description = "Name of bucket (container) with state file"
  type = string
}

variable account_resource_group {
  description = "Resource group for all resources within the account"
  type = string
}

# Nhais config variables

variable nhais_replicas {
  type = number
  default = 1
  description = "Number of service replicas in AKS cluster"
}

variable nhais_image {
  type = string
  description = "Url or tag in docker hub for NHAIS docker image"
  default = "nhsdev/nia-nhais-adaptor:1.4.1"
}

variable nhais_application_port {
  type = number
  description = "Port of which the the service should be visible, also the port used by LB if set"
  default = 8080
}

variable nhais_container_port {
  type = number
  description = "Port exposed on the container"
  default = 8080
}
