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
  default = 80
}

variable nhais_container_port {
  type = number
  description = "Port exposed on the container"
  default = 8080
}

variable nhais_mesh_mailbox_id {
  type = string
  default = "gp_mailbox"
}

variable nhais_mesh_mailbox_password {
  type = string
}

variable nhais_mesh_shared_key {
  type = string
  default = "SharedKey"
}

variable nhais_mesh_host {
  type = string
  default = "https://fake-mesh:8829/messageexchange/"
}

variable nhais_mesh_cert_validation {
  type = bool
  default = false
}

variable nhais_mesh_endpoint_cert {
  type = string
}

variable nhais_mesh_endpoint_private_key {
  type = string
}

variable nhais_mesh_sub_ca {
  type = string
}

variable nhais_mesh_recipient_mailbox_id_mappings {
  type = string
}

variable nhais_mesh_polling_cycle_minimum_interval_in_seconds {
  type = number
  default = 300
}

variable nhais_mesh_client_wakeup_interval_in_miliseconds {
  type = number
  default = 60000
}

variable nhais_scheduler_enabled {
  type = bool
  default = true
}

variable nhais_lb_ip {
  type = string
  default = ""
}

variable base_ptl_dns_servers {
  type = list(string)
  default = []
  description = "IP of DNS Servers to use in PTL"
}

# fake_mesh

variable fake_mesh_in_use {
  default = true
  type = bool
}

variable fake_mesh_container_port {
  type = number
  default = 8829
}

variable fake_mesh_application_port {
  type = number
  default = 8829
}

variable fake_mesh_image {
  type = string
  default = "nhsdev/fake-mesh:0.2.0"
}
