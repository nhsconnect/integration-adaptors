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
  default = "gp2gp"
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


# GP2GP config variables

variable "gp2gp_image" {
  type = string
  description = "Url or tag in docker hub for GP2GP docker image"
  default = "nhsdev/nia-gp2gp-adaptor:1.1.2"
}

variable "gp2gp_replicas" {
  type = number
  default = 1
  description = "Number of service replicas in AKS cluster"
}

variable "gp2gp_amqp_max_redeliveries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "gp2gp_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}

variable "gp2gp_log_level" {
  type = string
  description = "Level of logging for GP2GP application"
  default = "INFO"
}

variable "gp2gp_gpc_override_nhs_number" {
  type = string
  description = "NHS Number override for patient transfer requests"
  default = ""
}

variable "gp2gp_gpc_override_to_asid" {
  type = string
  description = "Override value to override to aside in GPC requests"
  default = ""
}

variable "gp2gp_gpc_override_from_asid" {
  type = string
  description = "Override value to override from aside in GPC requests"
  default = ""
}


variable "gp2gp_application_port" {
  type = number
  description = "Port of which the the service should be visible, also the port used by LB if set"
  default = 80
}

variable "gp2gp_container_port" {
  type = number
  description = "Port exposed on the container"
  default = 8080
}

variable "gp2gp_gpc_get_structured_endpoint" {
  type = string
  description = "Endpoint for GPC access structured request"
  default = "/fhir/Patient/$gpc.getstructuredrecord"
}

variable "gp2gp_gpc_get_document_endpoint" {
  type = string
  description = "Endpoint for GPC access document request"
  default =  "/fhir/Binary/"
}

variable "gp2gp_gpc_host" {
  type = string
  description = "Host used for GPC requests"
  default = "orange.testlab.nhs.uk"
}
