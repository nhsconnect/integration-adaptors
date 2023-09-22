variable "account_id" {
  type = string
  description = "ID of AWS Account on which the resources are created"
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

variable "region" {
  type = string
  description = "Region where the resources will be created"
}

variable "base_cidr_block" {
  type = string
  description = "CIDR block to use for VPC"
}

variable "tf_state_bucket" {
  type = string
  description = "Name of S3 bucket with TF state of components"
}

variable "pss_logs_datetime_format" {
  type = string
  description = "Format for date and time in logs"
  default = "%Y-%m-%d %H:%M:%S%L"
}

variable "pss_service_desired_count" {
  type = number
  description = "Number of containers to run in the service"
}

variable "pss_service_minimal_count" {
  type = number
  description = "Minimal number of containers to run in the service"
}

variable "pss_service_maximal_count" {
  type = number
  description = "Maximal number of containers to run in the service"
}

variable "pss_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
}

variable "protocol" {
  type = string
  description = "Protocol used by container"
  default = "tcp"
}

variable "pss_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "pss_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

variable "enable_dlt" {
  type = bool
  description = "Should the containers in the service be attached to dlt"
  default = false
}

variable "dlt_vpc_id" {
  type = string
  description = "VPC where Distributed Load testing environment is hosted"
  default = ""
}
variable "pss_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "pss_log_level" {
  type = string
  description = "Level of logging for pss application"
}

variable "pss_healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
  default = "/healthcheck"
}

variable "pss_amqp_max_redeliveries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "pss_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "pss_gp2gp_translator_testbox" {
  type = bool
  description = "Should en EC2 instance be created along the containers (with the same same subnet and security group) Useful for testing connectivity"
  default = false
}

variable "pss_gpc_facade_testbox" {
  type = bool
  description = "Should en EC2 instance be created along the containers (with the same same subnet and security group) Useful for testing connectivity"
  default = false
}

variable "create_pss_testbox" {
  type = bool
  default = false
}

# Variables related to PTL connectivity

variable "ptl_connected" {
  type = string
  description = "Should this environment be connected to NHS PTL"
  default = false
}

# MHS mock specific variables 
variable "pss_mock_mhs_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 8080
}

variable "pss_create_mhs_mock" {
  type = bool
  default = false
  description = "Should an MHS mock be created and used by pss"
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

variable "pss_gp2gp_inbound_queue_name" {
  type = string
  description = "The name of the queue to forward daisy chained messages to"
  default = "gp2gpInboundQueue"
}

variable "daisy_chaining_active" {
  type = bool
  description = "Is daisy chaining (gp2gp adaptor message forwarding) enabled"
  default = false
}

variable "secret_name_sds_apikey" {
  type = string
  description = "SDS API Key"
}

variable "supported_file_types" {
  type = string
  description = "The attachment MIME types supported"
  default = "application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msoutlook,text/rtf,text/plain,image/bmp,image/gif,image/jpeg,image/png,image/tiff,application/xml,audio/x-aiff,audio/x-mpegurl,audio/mpeg,audio/x-wav,audio/x-ms-wma,video/3gpp2,video/3gpp,video/x-ms-asf,video/x-ms-asf,video/x-msvideo,video/x-flv,video/quicktime,video/mp4,video/mpeg,audio/vnd.rn-realaudio,application/x-shockwave-flash,video/x-ms-vob,video/x-ms-wmv,application/postscript,application/postscript,image/svg+xml,image/x-pict,application/pdf,application/vnd.openxmlformats-package.relationships+xml,text/css,text/html,application/xhtml+xml,text/plain,application/json,text/xml,application/xml,application/pdf,audio/basic,audio/mpeg,image/png,image/gif,image/jpeg,image/tiff,video/mpeg,application/msword,application/octet-stream,text/csv,application/dicom,application/zip,application/x-rar-compressed,application/x-gzip,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/x-mplayer2,audio/x-au,application/x-troff-msvideo,video/msvideo,image/x-windows-bmp,application/pkix-cert,application/x-x509-ca-cert,application/cdf,application/x-cdf,application/x-netcdf,application/x-x509-user-cert,application/EDIFACT,application/EDI-X12,application/EDI-Consent,application/hl7-v2,application/hl7-v2+xml,video/x-mpeg,application/pkcs10,application/x-pkcs10,application/pkcs-12,application/x-pkcs12,application/x-pkcs7-signature,application/pkcs7-mime,application/x-pkcs7-mime,application/pkcs7-mime,application/x-pkcs7-mime,application/x-pkcs7-certreqresp,application/pkcs7-signature,application/x-rtf,application/x-compressed,application/x-zip-compressed,multipart/x-zip,application/pgp,application/pgp-keys,application/pgp-signature,application/x-pgp-plugin,application/pgp-encrypted,audio/wav,audio/wave,audio/x-pn-wav,chemical/x-mdl-sdfile,chemical/x-mdl-molfile,chemical/x-pdb,application/x-hl7"
}
