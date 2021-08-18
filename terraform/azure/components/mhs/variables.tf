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
  default = "mhs"
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


# MHS Global config variables

variable "mhs_log_level" {
  type = string
  description = "Level of logging for mhs application"
  default = "INFO"
}

variable "mhs_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 80
}

variable "mhs_service_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 80
}


# MHS-INBOUND SPECIFIC
variable "mhs-inbound_image" {
  description = "MHS-INBOUND Image Name"
  type = string
  default = "nhsdev/nia-mhs-inbound:1.0.2"
}

variable "mhs_inbound_service_container_port" {
  type = number
}

variable mhs_inbound_queue_name {
  type = string
  description = "Name of queue used by MHS Inbound"
  default = "build1_mhs_inbound"
}

variable "mhs_inbound_use_ssl" {
  type = bool
  default = true
}

# MHS-OUTBOUND SPECIFIC
variable "mhs_outbound_service_container_port" {
  type = number
}

variable "mhs-outbound_image" {
  description = "MHS-OUTBOUND Image Name"
  type = string
  default = "nhsdev/nia-mhs-outbound:1.0.2"
}

variable "mhs_outbound_forward_reliable_url" {
  type = string
  default = ""
}

variable "mhs_outbound_validate_certificate" {
  type = bool
  default = false
}

variable "mhs_spine_org_code" {
  type = string
  default = "YES"
}

variable "mhs_outbound_spineroutelookup_validate_certificate" {
  type = bool
  default = false
}





# MHS-ROUTE SPECIFIC
variable "mhs_route_service_container_port" {
  type = number
}

variable "mhs-route_image" {
  description = "MHS-ROUTE Image Name"
  type = string
  default = "nhsdev/nia-mhs-route:1.0.2"
}

variable "mhs_route_disable_sds_tls" {
  type = bool
  default = false
}

variable "mhs_route_redis_disable_tls" {
  type = bool
  default = true
}

variable "mhs_route_sds_search_base" {
  type = string
  default = "ou=services,o=nhs"
}

variable "mhs_route_sds_url" {
  type = string
  default = ""
}




# secret names
# Define the names of secrets in secret manager for secret variables used by mhs
# These are different depending on the way MHS is connected to NHS systems

variable mhs_party_key {
  type = string
  default = "opentest-party-key"
}

variable mhs_client_cert {
  type = string
  default = "opentest-client-certificate"
}

variable mhs_client_key {
  type = string
  default = "opentest-client-key"
}

variable mhs_ca_certs {
  type = string
  default = "opentest-ca-certs"
}

variable mhs_spine_route_lookup_ca_certs {
  type = string
  default = "build-outbound-route-connection-cacerts"
}
