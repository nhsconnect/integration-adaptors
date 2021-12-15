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
  default = 80
}

variable "pss_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

variable "pss_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "pss_log_level" {
  type = string
  description = "Level of logging for PSS application"
  default = "INFO"
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
}

variable "pss_gpc_facade_testbox" {
  type = bool
  description = "Should en EC2 instance be created along the containers (with the same same subnet and security group) Useful for testing connectivity"
}

variable "pss_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "postgres_master_password" {
  type = string
  description = "master password for postgres server"
}

# Variables related to PTL connectivity

variable "ptl_connected" {
  type = bool
  description = "Should this environment be connected to NHS PTL"
  default = false
}

# MHS mock specific variables 
variable "pss_mock_mhs_port" {
  type = number
  default = 8080
  description = "Port Number on which service within container will be listening"
}

variable "pss_create_mhs_mock" {
  type = bool
  default = true
  description = "Should an MHS mock be created and used by pss"
}

# GPC API Facade specific variables 
variable "pss_gpc_api_facade_container_port" {
  type = number
  default = 8080
  description = "Port Number on which service within container will be listening"
}

# GP2GP Translator specific variables 
variable "pss_gp2gp_translator_container_port" {
  type = number
  default = 8080
  description = "Port Number on which service within container will be listening"
}
