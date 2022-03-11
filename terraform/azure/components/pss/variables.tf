## Azure config variables ##
variable "client_id" {
    type = string
    description = "Azure Client ID to be used as Service Principal to create Azure Kubernetes Cluster"
    default = ""
}

variable "client_secret" {
    type = string
    description = "Azure Client SECRET to be used as Service Principal to create Azure Kubernetes Cluster"
    default = ""
}

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
  default = "pss"
}

variable "location" {
  type = string
  description = "Azure Location (Region)"
}

variable "state_bucket_resource_group" {
  description = "Resource group which contains bucket with TF state file"
  type = string
}

variable "state_bucket_storage_account" {
  description = "Name of storage account with TF state bucket"
  type = string
}

variable "state_bucket_name" {
  description = "Name of bucket (container) with state file"
  type = string
}

variable "account_resource_group" {
  description = "Resource group for all resources within the account"
  type = string
}


# PSS config variables

variable "pss_image" {
  type = string
  description = "Url or tag in docker hub for pss docker image"
  default = "nhsdev/nia-gp2gp-adaptor:1.1.2"
}

variable "pss_replicas" {
  type = number
  default = 1
  description = "Number of service replicas in AKS cluster"
}

variable "pss_amqp_max_redeliveries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "pss_log_level" {
  type = string
  description = "Level of logging for GP2GP application"
  default = "INFO"
}

variable "pss_application_port" {
  type = number
  description = "Port of which the the service should be visible, also the port used by LB if set"
  default = 80
}


# MHS mock specific variables 
variable "pss_mock_mhs_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 8080
}

# GPC API Facade specific variables 
variable "pss_gpc_api_facade_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 8081
}

# GP2GP Translator specific variables 
variable "pss_gp2gp_translator_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 8085
}