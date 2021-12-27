variable "project" {
  type = string
  description = "(Required) Name of the project where this module is used"
}

variable "environment" {
  type = string
  description = "(Required) Name of the environment where this modules is used"
}

variable "component" {
  type = string
  description = "Name of the component where the module is used"
}

variable "region" {
  type = string
  description = "Region where the resources will be created"
}

variable "module_name" {
  type = string
  description = "(Static) Name of this module"
  default = "ecs_service"
}

variable "module_instance" {
  type = string
  description = "(Required) Name of the instance of this module"
}

variable "default_tags" {
  type = map(string)
  description = "List of tags to add to resources in module"
}

variable "availability_zones" {
  type = list(string)
  description = "List of availabilty zones to be used by this module"
}

variable "cluster_id" {
  type = string
  description = "(Required) ID of the cluster to run the service on"
}

variable "maximal_count" {
  type = number
  description = "(Required) Maximal Number of containers to run in the service"
}

variable "desired_count" {
  type = number
  description = "(Required) Number of containers to run in the service"
}

variable "minimal_count" {
  type = number
  description = "Minimal count of containers"
  default = 0
}

variable "container_port" {
  type = number
  description = "(Required) Port Number on which service within container will be listening"
}

variable "application_port" {
  type = number
  description = "(Optional) Port Number on which the load balancer should be listening, default is 80"
  default = 80
}

variable "container_healthcheck_port" {
  type = number
  description = "(Optional) Port number on which the container provides info about it's healthcheck, 0 indicates the same port as container port"
}

variable "container_protocol" {
  type = string
  description = "Protocol used by container 99% of cases TCP"
  default = "tcp"
}

variable "health_check_grace_period" {
  type = number
  description = "(Optional) Seconds to ignore failing load balancer health checks on newly instantiated tasks to prevent premature shutdown, up to 2147483647. Only valid for services configured to use load balancers."
  default = 30
}

variable "launch_type" {
  type = string
  description = "(Optional) Type of cluster on which this service will be run, FARGATE or EC2, default is EC2"
  default = "EC2"
}

variable "scheduling_strategy" {
  type = string
  description = "(Optional) The scheduling strategy to use for the service. The valid values are REPLICA and DAEMON. Defaults to REPLICA"
  default = "REPLICA"
}

variable "deployment_maximum_percent" {
  type = number
  description = "Optional) The upper limit (as a percentage of the service's desiredCount) of the number of running tasks that can be running in a service during a deployment. Not valid when using the DAEMON scheduling strategy."
  default = 200
}

variable "deployment_minimum_healthy_percent" {
  type = number
  description = "(Optional) The lower limit (as a percentage of the service's desiredCount) of the number of running tasks that must remain running and healthy in a service during a deployment. "
  default = 100
}

variable "assign_public_ip" {
  type = bool
  description = "(Optional) Should the container isntance have a public IP adress"
  default = false
}

variable "additional_security_groups" {
  type = list(string)
  description = "(Optional) List of ids of additional SGs to which the service should belong"
  default = []
}

variable "vpc_id" {
  type = string
  description = "(Required) ID of VPC in which this service will be running"
}

variable "lb_subnet_ids" {
  type = list(string)
  description = "(Requred) List of SubnetIds for subnets which this service Load Balancer will use"
}

variable "container_subnet_ids" {
  type = list(string)
  description = "(Requred) List of SubnetIds for subnets which this service Containers will use"
}

variable "image_name" {
  type = string
  description = "Path to docker image to be used in task definition"
}

variable "cpu_units" {
  type = number
  description = "Number of CPU units to assign to containers"
  default = 2048
}

variable "memory_units" {
  type = number
  description = "Number of Memory units to assign to containers"
  default = 4096
}

variable "network_mode" {
  type = string
  description = "Network mode for containers"
  default = "awsvpc"
}

variable "logs_retention" {
  type = number
  description = "Number of days to keep the logs in CloudWatch"
  default = 30
}

variable "log_stream_prefix" {
  type = string
  description = "Value for logs stream prefix"
}

variable "logs_datetime_format" {
  type = string
  description = "Format for date and time in logs"
  default = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
}

variable "enable_load_balancing" {
  type = bool
  description = "Should the containers in the service be attached to loadbalancer"
  default = true
}

variable "enable_dlt" {
  type = bool
  description = "Should the containers in the service be attached to dlt"
}

variable "dlt_vpc_id" {
  type = string
  description = "VPC where Distributed Load testing environment is hosted"
  default = ""
}

variable "load_balancer_type" {
  type = string
  description = "Type of loadbalancer for service, application or network"
  default = "application"
}

variable "use_application_lb" {
  type = bool
  description = "True if the LB should be application type"
  default = true
}

variable "use_network_lb" {
  type = bool
  description = "True if the LB should be network type"
  default = false
}

variable "protocol" {
  type = string
  description = "Protocol for load balancer, HTTP or HTTPS"
  default = "HTTP"
}

variable "health_check_grace_period_seconds" {
  type = number
  description = "Seconds to ignore failing load balancer health checks on newly instantiated tasks to prevent premature shutdown"
  default = 20
}

variable "environment_variables" {
  type = list(object({name=string, value=string}))
  description = "List of objects for Environment variables"
  default = []
}

variable "command_variables" {
  type = list(string)
  description = "list of objects for commands to pass to container"
  default = []
}

variable "secret_variables" {
  type = list(object({name=string, valueFrom=string}))
  description = "list of objects for secret variables to pass to container"
  default = []
}

variable "task_execution_role_arn" {
  type = string
  description = "ARN of role used by the ECS Task"
}

variable "task_role_arn" {
  type = string
  description = "ARN of role used by the container itself"
}

variable "task_scaling_role_arn" {
  type = string
  description = "ARN of role used to autoscale the task"
}

variable "service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "healthcheck_path" {
  type = string
  description = "Path on which the container provides info about its status"
}

variable "deregistration_delay" {
  type = number
  description = "Time for draining connection before switching off the container, AWS Default is 300s, ours is 45s"
  default = 45
}

variable "lb_allowed_security_groups" {
  type = list(string)
  description = "List of SG IDs that will be allowed to access the Load Balancer"
  default = []
}

variable "lb_allowed_cidrs" {
  type = list(string)
  description = "List of CIDRs that will be allowed to access the Load Balancer"
  default = []
}

variable "container_allowed_security_groups" {
  type = list(string)
  description = "List of SG IDs that will be allowed to access the container(s)"
  default = []
}

variable "container_allowed_cidrs" {
  type = list(string)
  description = "List of CIDRs that will be allowed to access the the container(s)"
  default = []
}

variable "create_testbox" {
  type = bool
  description = "Should the module contain EC2 instance for connectivity testing"
  default = false
}

variable "jumpbox_sg_id" {
  type = string
  default = ""
  description = "SG of Account jumpbox to allow traffic in"
}

variable "multiple_cointainers" {
  type = bool
  default = false
  description = "Indicates that the service and task will host multiple containers"
}

variable "additional_container_config" {
  type = list(any)
  default = []
  description = "Object (later converted to json) with configuration for additional containers"
}

variable private_ips_for_lb {
  type = list(string)
  description = "List of Private IPs to assign to LB Fronenteds, should match the subnets, if there is more subnets than entries here, the remaining subnets will get random IP"
  default = []
}
