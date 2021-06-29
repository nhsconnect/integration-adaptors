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
  default = "lab-results"
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

# Lab-Results config variables

variable "lab-results_mesh_mailbox_id" {
  type = string
  default = "gp_mailbox"
}

variable "lab-results_mesh_mailbox_password" {
  type = string
}

variable "lab-results_mesh_shared_key" {
  type = string
  default = "SharedKey"
}

variable "lab-results_mesh_sub_ca" {
  type = string
}

variable "lab-results_mesh_endpoint_cert" {
  type = string
}

variable "lab-results_mesh_endpoint_private_key" {
  type = string
}

variable "lab-results_mesh_recipient_mailbox_id_mappings" {
  type = string
}

variable "lab-results_ssl_trust_store_password" {
  type = string
}

variable "lab-results_replicas" {
  type = number
  default = 1
  description = "Number of service replicas in AKS cluster"
}

variable "lab-results_image" {
  type = string
  description = "Url or tag in docker hub for LAB-RESULTS docker image"
  default = "nhsdev/nia-lab-results-adaptor:0.0.4"
}

variable "lab-results_application_port" {
  type = number
  description = "Port of which the the service should be visible, also the port used by LB if set"
  default = 80
}

variable "lab-results_container_port" {
  type = number
  description = "Port exposed on the container"
  default = 8080
}

variable "lab-results_mesh_host" {
  type = string
  default = "https://fake-mesh:8829/messageexchange/"
}

variable "lab-results_mesh_cert_validation" {
  type = bool
  default = false
}

variable "lab-results_amqp_max_redeliveries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "lab-results_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}

variable "lab-results_log_level" {
  type = string
  description = "Level of logging for LAB_RESULTS application"
  default = "INFO"
}

variable "lab-results_mesh_polling_cycle_minimum_interval_in_seconds" {
  type = number
  default = 300
}

variable "lab-results_mesh_client_wakeup_interval_in_miliseconds" {
  type = number
  default = 60000
}

variable "lab-results_mesh_polling_cycle_duration_in_seconds" {
  type = number
  description = "Duration of mesh polling cycle"
  default = 285
}

variable "lab-results_scheduler_enabled" {
  type = bool
  default = true
}

variable "lab-results_ssl_trust_store_url" {
  type = string
  default= ""
}

variable "lab-results_lb_ip" {
  type = string
  default = ""
}

variable "base_ptl_dns_servers" {
  type = list(string)
  default = []
  description = "IP of DNS Servers to use in PTL"
}

# fake_mesh

variable lab-results_fake_mesh_in_use {
  default = true
  type = bool
}

variable lab-results_fake_mesh_container_port {
  type = number
  default = 8829
}

variable lab-results_fake_mesh_application_port {
  type = number
  default = 8829
}

variable lab-results_fake_mesh_image {
  type = string
  default = "nhsdev/fake-mesh:0.2.0"
}
