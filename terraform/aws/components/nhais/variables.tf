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
  default = "nhais"
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

variable "nhais_service_desired_count" {
  type = number
  description = "Number of containers to run in the service"
}

variable "nhais_service_minimal_count" {
  type = number
  description = "Minimal number of containers to run in the service"
}

variable "nhais_service_maximal_count" {
  type = number
  description = "Maximal number of containers to run in the service"
}

variable "nhais_service_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
}

variable "nhais_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 80
}

variable "nhais_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "nhais_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

variable "nhais_mongo_options" {
  type = string
  description = "Options for Mongo"
}

variable "nhais_mongo_documentdb_tls_enabled" {
  type = string
  description = "Enable TLS on AWS Document DB"
}

variable "nhais_mongo_trust_store_path" {
  type = string
  description = "S3 path to the custom trust store"
  default = ""
}

variable "nhais_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "nhais_log_level" {
  type = string
  description = "Level of logging for NHAIS application"
  default = "INFO"
}

variable "nhais_healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
  default = "/healthcheck"
}

variable "nhais_amqp_max_retries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "nhais_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}

variable "nhais_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "dlt_vpc_id" {
  type = string
  description = "VPC where Distributed Load testing environment is hosted"
  default = ""
}

variable "enable_dlt" {
  type = bool
  description = "Should the containers in the service be attached to dlt"
}

variable "create_testbox" {
  type = bool
  default = false
  description = "Should en EC2 instance be created along the containers (with the same same subnet and security group) Useful for testing connectivity"
}

# Variables related to PTL connectivity

variable "ptl_connected" {
  type = bool
  description = "Should this environment be connected to NHS PTL"
  default = false
}

# Variables for MESH mailbox

variable "nhais_mesh_host" {
  type = string
  description = "URL for MESH host"
  default = ""
}

variable "nhais_mesh_cert_validation" {
  type = string
  description = "false will disable certificate validation for SSL connection"
  default = "true"
}

variable "nhais_mesh_polling_cycle_minimum_interval_in_seconds" {
  type = number
  description = "Delay in seconds on scanning mesh mailbox"
  default = 300
}

variable "nhais_mesh_client_wakeup_interval_in_milliseconds" {
  type = number
  description = "Interval in miliseconds between mailbox scans"
  default = 60000
}

variable "nhais_mesh_polling_cycle_duration_in_seconds" {
  type = number
  description = "Duration of mesh polling cycle"
  default = 285
}

variable "nhais_scheduler_enabled" {
  type = bool
  description = "Enable scheduler"
  default = true
}
