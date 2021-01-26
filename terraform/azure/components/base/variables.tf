## Azure config variables ##
variable "client_id" {}

variable "client_secret" {}

variable location {
  description "Azure Location (Region)"
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

## Resource group variables ##
variable resource_group_name {
  default = "nia-base-rg"
}

variable jumpbox_user {
  default = "mhs_user"
}

variable "nia_vnet_cidr" {
  default = "10.20.0.0/16"
}

variable "jumpbox_subnet_cidr" {
  default = "10.20.1.0/24"
}

variable "secret_jumpbox_allowed_ips" {
  description = "List of IPs that should be allowed to jumpbox, this value is not stored in Azure Keyvault and should always be loaded from tfvars"
  default = []
}
