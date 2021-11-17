## Azure config variables ##
variable "client_id" {}

variable "client_secret" {}

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
  default = "base"
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

variable private_cluster {
  description = "Should the AKS cluster be private"
  default = true
  type = bool
}

variable dns_prefix {
  default = "nia"
  type = string
}

variable "base_cidr" {
  type = string
  description = "CIDR for vnet in base component"
}

variable base_redis_cidr {
  type = string
  description = "CIDR used by base redis"
}

variable "base_aks_cidr" {
  type = string
  description = "CIDR for aks cluster"
}

variable "base_aks_internal_cidr" {
  type = string
  description = "CIDR used internally by AKS"
  default = "10.30.0.0/16"
}

variable "base_aks_internal_dns" {
  default = "10.30.0.10"
}

variable "base_aks_docker_bridge_cidr" {
  default = "10.31.0.5/16"
}

variable "ptl_connected" {
  type = bool
  default = false
  description = "Is the environment connected to NHS PTL (HSCN)"
}

variable "ptl_cidr" {
  type = string
  default = ""
  description = "CIDR assigned to us by NHS, used for PTL peering / VPN"
}

variable base_ptl_prefixes {
  type = list(string)
  default = []
  description = "Prefixes in form of CIDR which should be routed via PTL connection"
}

variable base_ptl_next_hop {
  type = string
  default = ""
  description = "IP of next hop router in PTL connection"
}

variable base_private_dns {
  type = string
}

## Resource group variables ##

variable jumpbox_user {
  default = "azure_user"
}

variable "base_testbox_storage_type" {
  type = string
  description = "Disk type for jumpbox, options are Standard_LRS, StandardSSD_LRS, and Premium_LRS"
  default = "Standard_LRS"
}

variable jumpbox_private_key_location {
  default = "~/.ssh/azure_mhs_jumpbox"
}

variable aks_admin_user {
  default = "aks_admin"
}

variable aks_node_count {
  default = 1
  type = number
}

variable "base_testbox_cidr" {
  type = string
  description = "CIDR for jumpbox subnet"
}

variable "jumpbox_allowed_ips" {
  description = "List of IPs that should be allowed to jumpbox, this value is not stored in Azure Keyvault and should always be loaded from tfvars"
  default = []
}

variable servicebus_sku {
  description = "Service level for Servicebus, available are Basic, Standard and Premium"
  type = string
  default = "Premium" # Standard is needed to support AMQP protocol, Premium to allow connection with Service Endpoint
}

variable servicebus_capacity {
  description = "Servicebus capacity"
  type = number
  default = 1 # has to be 0 for Basic and Standard SKU, Premium SKU allows for more
}
