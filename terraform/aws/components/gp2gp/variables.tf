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
  default = "gp2gp"
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

variable "gp2gp_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "gp2gp_gpcc_mock_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
  default = "main-340-4d6ff67"
}

variable "gp2gp_mhs_mock_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
  default = "main-341-b4b28a1"
}

variable "gp2gp_gpcapi_mock_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
  default = "main-340-4d6ff67"
}
variable "gp2gp_sdsapi_mock_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
  default = "main-340-4d6ff67"
}

variable "gp2gp_service_desired_count" {
  type = number
  description = "Number of containers to run in the service"
}

variable "gp2gp_service_minimal_count" {
  type = number
  description = "Minimal number of containers to run in the service"
}

variable "gp2gp_service_maximal_count" {
  type = number
  description = "Maximal number of containers to run in the service"
}

variable "gp2gp_service_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
}

variable "gp2gp_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 80
}

variable "gp2gp_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

# variable "gp2gp_mongo_options" {
#   type = string
#   description = "Options for Mongo"
#   default = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
# }

variable "dlt_vpc_id" {
  type = string
  description = "VPC where Distributed Load testing environment is hosted"
  default = ""
}

variable "enable_dlt" {
  type = bool
  description = "Should the containers in the service be attached to dlt"
  default = false
}

variable "gp2gp_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "gp2gp_log_level" {
  type = string
  description = "Level of logging for gp2gp application"
  default = "INFO"
}

variable "gp2gp_healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
  default = "/healthcheck"
}

variable "gp2gp_amqp_max_retries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "gp2gp_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}

variable "gp2gp_gpc_get_url" {
  type = string
  description = "URL used for GPC requests"
  default = "https://orange.testlab.nhs.uk/B82617/STU3/1/gpconnect"
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

variable "gp2gp_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "gp2gp_extract_cache_bucket_retention_period" {
  type = number
  description = "Number of days objects will be retained in gp2gp_extract_cache_bucket"
  default = 7
}

variable "gp2gp_logs_datetime_format" {
  type = string
  description = "Format for date and time in AWS cloudwatch logs"
  default = "%Y-%m-%d %H:%M:%S%L"
}

variable gp2gp_mongo_options {
  type = string
  description = "Options for mongo db connection"
}

variable gp2gp_ssl_trust_store_url {
  type = string
  description = "URL to bucket with trusted CAs"
  default = ""
}

variable mhs_inbound_queue_name {
  type = string
  description = "Name of queue used by MHS Inbound "
}

variable "create_testbox" {
  type = bool
  default = false
  description = "Should en EC2 instance be created along the containers (with the same same subnet and security group) Useful for testing connectivity"
}

variable "gp2gp_create_mhs_mock" {
  type = bool
  default = false
  description = "Should an MHS mock be created and used by GP2GP"
}

variable "gp2gp_create_gpcc_mock" {
  type = bool
  default = false
  description = "Should GPCC mock be created and used by GP2GP"
}

variable "gp2gp_create_sdsapi_mock" {
  type = bool
  default = false
  description = "Should SDS API GPCC mock be created and used by GP2GP"
}

variable "gp2gp_create_gpcapi_mock" {
  type = bool
  default = false
  description = "Should GPConnect API mock be created and used by GP2GP"
}

variable "gp2gp_mock_mhs_port" {
  type = number
  default = 8081
}

variable gp2gp_mock_mhs_amqp_max_redeliveries {
  type = number
  default = 15
}

variable "gp2gp_create_wiremock" {
  type = bool
  default = false
  description = "Should an wiremock mock be created and used by GP2GP"
}

variable "gp2gp_wiremock_container_port" {
  type = number
  default = 8080
}

variable "gp2gp_wiremock_application_port" {
  type = number
  default = 8080
}

variable "gp2gp_mock_port" {
  type = number
  default = 8080
  description = "Application/Container port number for GPCC_MOCK, GPC-API_MOCK, SDS_API_MOCK"
}

variable gp2gp_gpc_override_nhs_number {
  type = string
  description = "NHS Number override for patient transfer requests"
  default = ""
}

variable gp2gp_gpc_override_to_asid {
  type = string
  description = "Override value to override to aside in GPC requests"
  default = ""
}

variable gp2gp_gpc_override_from_asid {
  type = string
  description = "Override value to override from aside in GPC requests"
  default = ""
}

# Variables related to PTL connectivity

variable "ptl_connected" {
  type = bool
  description = "Should this environment be connected to NHS PTL"
  default = false
}
