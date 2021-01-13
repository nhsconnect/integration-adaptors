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
  default = "mhs"
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

variable "mhs_build_id" {
  type = string
  description = "Number of the current build, used for tagging the logs"
}

variable "mhs_service_desired_count" {
  type = number
  description = "Number of containers to run in the service"
}

variable "mhs_service_minimal_count" {
  type = number
  description = "Minimal number of containers to run in the service"
}

variable "mhs_service_maximal_count" {
  type = number
  description = "Maximal number of containers to run in the service"
}

variable "mhs_service_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
}

variable "mhs_service_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 80
}

variable "mhs_nginx_container_port" {
  type = number
  description = "Port Number on which service within container will be listening"
  default = 443
}

variable "mhs_nginx_application_port" {
  type = number
  description = "Port number on which the service load balancer will listen"
  default = 443
}

variable "mhs_service_launch_type" {
  type = string
  description = "Type of cluster on which this service will be run, FARGATE or EC2"
}

variable "mq_broker_name" {
  type = string
  description = "Name of the MQ broker shared between all envs"
}

# variable "mhs_mongo_options" {
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

variable "mhs_environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "mhs_log_level" {
  type = string
  description = "Level of logging for mhs application"
  default = "INFO"
}

variable "mhs_healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
  default = "/actuator/health"
}

variable "mhs_amqp_max_retries" {
  type = number
  description = "Max retries on connection to amqp"
  default = 3
}

variable "mhs_amqp_retry_delay" {
  type = number
  description = "Delay on retries to connect to amqp"
  default = 100
}
variable "mhs_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
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

# outbound specific

variable "mhs_outbound_validate_certificate" {
  type = bool
  default = true
}

variable "mhs_outbound_spineroutelookup_verify_certificate" {
  type = bool
  default = true
}


# route specific

variable "mhs_route_sds_url" {
  type = string
  default = ""
}

variable "mhs_route_disable_sds_tls" {
  type = bool
  default = true
}
variable "mhs_route_sds_search_base" {
  type = string
  default = "ou=services,o=nhs"
}


# inbound specific