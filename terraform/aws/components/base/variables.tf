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
  default = "base"
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

variable "cluster_container_insights" {
  type = string
  description = "Container Insights for containers in the cluster, default is disabled"
  default = "disabled"
}

variable "mq_vpc_id" {
  type = string
  description = "VPC where MQ cluster is hosted"
}

variable "enable_internet_access" {
  type = bool
  description = "Enables internet access from private subnets by adding a route table to NAT Gateway"
  default = false
}

variable "root_domain" {
  type = string
  description = "Name of the domain in which route53 records will be added"
}
