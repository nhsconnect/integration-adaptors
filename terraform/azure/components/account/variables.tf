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

variable account_bucket_storage_account {
  description = "Name of storage account for buckets being used by Adapters"
  type = string
}

variable "account_cidr" {
  type = string
  description = "CIDR for vnet in account component"
}

variable account_firewall_cidr {
  type = string
  description = "CIDR used by account firewall"
}

variable "account_jumpbox_cidr" {
  type = string
  description = "CIDR for jumpbox subnet"
}

variable "account_jumpbox_storage_type" {
  type = string
  description = "Disk type for jumpbox, options are Standard_LRS, StandardSSD_LRS, and Premium_LRS"
  default = "Standard_LRS"
}

variable "jumpbox_allowed_ips" {
  description = "List of IPs that should be allowed to jumpbox, this value is not stored in Azure Keyvault and should always be loaded from tfvars"
  default = []
}

variable jumpbox_user {
  default = "azure_user"
}

variable jumpbox_private_key_location {
  default = "~/.ssh/azure_mhs_jumpbox"
}

variable additional_keyvault_tenants {
  type = list(
    object({
      object_id = string
      tenant_id = string
    })
  )
  default = []
}
