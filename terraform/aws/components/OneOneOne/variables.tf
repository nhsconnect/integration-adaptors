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
  default = "OneOneOne"
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

variable "OneOneOne_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "OneOneOne_service_desired_count" {
  type = number
  description = "Number of containers to run in the service"
}

variable "OneOneOne_service_minimal_count" {
  type = number
  description = "Minimal number of containers to run in the service"
}

variable "OneOneOne_service_maximal_count" {
  type = number
  description = "Maximal number of containers to run in the service"
}

variable "OneOneOne_service_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
}

variable "OneOneOne_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 80
}

variable "OneOneOne_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

# variable "OneOneOne_mongo_options" {
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

variable "OneOneOne_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "OneOneOne_log_level" {
  type = string
  description = "Level of logging for OneOneOne application"
  default = "INFO"
}

variable "OneOneOne_healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
  default = "/actuator/health"
}

variable "OneOneOne_amqp_max_retries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "OneOneOne_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}
variable "OneOneOne_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}