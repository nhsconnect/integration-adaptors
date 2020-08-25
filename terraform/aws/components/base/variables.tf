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

variable "dlt_vpc_id" {
  type = string
  description = "VPC where Distributed Load testing environment is hosted"
  default = ""
}

variable "second_dlt_route_id" {
  type = string
  description = "As the DLT has two route tables, this is the ID from the second route table which will be stated in Global.tfvars"
  default = ""
  }

variable "enable_dlt" {
  type = bool
  description = "Should the containers in the service be attached to dlt"
}

variable "mq_sg_id" {
  type = string
  description = "ID of SG attached to MQ cluster"
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


# Variables related to DocSB

variable "docdb_master_user" {
  type = string
  description = "Username for Document DB master user"
}

variable "docdb_master_password" {
  type = string
  description = "Password for Document DB master user"
}

variable "docdb_tls" {
  type = string
  default = "enabled"
  description = "Should the Document DB have a TLS enabled for incomming connections"
}

variable "docdb_audit_logs" {
  type = string
  default = "disabled"
  description = "Should audit logs be enabled for Document DB"
}

variable "docdb_retention_period" {
  type = number
  description = "How many days should the backups be kept, default is 1 day"
  default = 1
}

variable "docdb_instance_class" {
  type = string
  description = "Instance size to be used to Document DB instances"
}

variable "docdb_instance_count" {
  type = number
  description = "Number of instances in Document DB cluster"
  default = 1
}

# Variables related to PTL connectivity

variable "ptl_connected" {
  type = bool
  description = "Should this environment be connected to NHS PTL"
  default = false
}

variable "ptl_vpn_gateway_id" {
  type = string
  description = "Id of already created and connected gateway, reusing one created by hand"
  default = ""
} 

variable "ptl_assigned_cidr" {
  type = string
  description = "CIDR assigned to us by NHS, will be used as secondary CIDR in vpc"
  default = ""
}

variable "ptl_dns_servers" {
  type = list(string)
  description = "DNS servers in the connected PTL environment"
}

variable "lb_reserved_ips" {
  type = list(string)
  description = "List of IPs that should be used for load balancer in components - required for async communication"
  default = []
}
