#GPC-CONSUMER VARIABLES

variable "gpc-consumer_image" {
  type = string
  description = "Url or tag in docker hub for GPC Consumer docker image"
  default = "nhsdev/nia-gpc-consumer-adaptor:0.1.5"
}

variable "gpc-consumer_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 8080
}

variable "gpc-consumer_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
}

variable "gpc-consumer_include_certs" {
  type = bool
  description = "If TRUE, GPCC Spine Certs & Key Secrets will be included in envrionment variables"
  default = false
}

variable "gpc-consumer_root_log_level" {
  type = string
  description = "Level of logging for entire application including third-party dependencies"
  default = "WARN"
}

variable "gpc-consumer_log_level" {
  type = string
  description = "Level of logging for GPC-CONSUMER application"
  default = "INFO"
}

variable "gpc-consumer_sds_url" {
  type = string
  description = "URL to the SDS API"
  default = 8080 
}

variable "gpc-consumer_supplier_ods_code" {
  type = string
  description = "GPC Supplier ODS code"
  default = ""
}

variable "gpc-consumer_ssp_fqdn" {
  type = string
  description = "FQDN for the SDS API"
  default = ""
}

variable "gpc_enable_sds" {
  type = string
  description = "Enable SDS for GPC requests"
  default = "true"
}


#GPC-CONSUMER CERTS
# These are different depending on the way MHS is connected to NHS systems

variable gpc-consumer_spine_client_cert {
  type = string
}

variable gpc-consumer_spine_client_key {
  type = string
}

variable gpc-consumer_spine_root_ca_cert {
  type = string
}

variable gpc-consumer_spine_sub_ca_cert {
  type = string
}

variable gpc-consumer_sds_apikey {
  type = string
}
