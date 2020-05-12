## Azure config variables ##
variable "client_id" {}

variable "client_secret" {}

variable location {
  default = "UK West"
}

## Resource group variables ##
variable resource_group_name {
  default = "mhs-rg"
}


## AKS kubernetes cluster variables ##
variable cluster_name {
  default = "mhs-adaptor"
}

variable "agent_count" {
  default = 3
}

variable "dns_prefix" {
  default = "mhs"
}

variable "admin_username" {
    default = "mhs"
}
