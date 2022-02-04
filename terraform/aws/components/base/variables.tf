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

variable "docdb_storage_encrypted" {
  type = string
  description = "Document DB Encryption-at-rest enablement"
  default = true
}
variable "docdb_kms_key_id" {
  type = string
  description = "ARN for AWS KMS Key to encrypt Document DB"
}

variable "mongo_ssl_enabled" {
  type = bool
  description = "Should the Document DB have a TLS enabled for incomming connections"
  default = true
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

variable "opentest_connected" {
  type = bool
  description = "Should this environment be connected to OpenTest"
  default = true
}

variable "opentest_vpc_id" {
  type = string
  description = "Id of vpc with opentest instance"
}

variable "opentest_sg_id" {
  type = string
  description = "Id of Opentest security group"
}

variable "jenkins_worker_sg_id" {
  type = string
  description = "Id of Jenkins-Worker security group"
}

variable "elasticache_node_type" {
  type = string
  default = "cache.t2.micro"
}

variable "create_opentest_instance" {
  type = bool
  default = false
}

variable "jumpbox_allowed_ssh" {
  type = list(string)
  description = "List of CIDR that are allowed to SSH to jumpbox"
  default = []
}

# Variables related to Postgres DB

variable "create_postgres_db" {
  type = bool
  description = "If PostgreSQL DB needs to be created"
  default = false
}

variable "enable_start_stop_scheduler" {
  type = bool
  description = "If stop and start schedule will enabled postgres instance for this env"
  default = false
}

variable "enable_postgres_scheduler" {
  type = bool
  description = "Adds a tag to the to instance to allow start and stop scheduler to work on it"
  default = false
}

variable "postgres_scheduler_stop_pattern" {
  type = string
  description = "Schedule what time to stop instance"
  default = ""
}

variable "postgres_scheduler_start_pattern" {
  type = string
  description = "Schedule what time to start instance"
  default = ""
}

variable "postgres_master_user" {
  type = string
  description = "Username for Postgres DB master user"
}

variable "postgres_master_password" {
  type = string
  description = "Password for Postgres DB master user"
}

variable "postgres_instance_class" {
  type = string
  description = "Instance size to be used to Document DB instances"
}

variable "postgres_instance_count" {
  type = number
  description = "Number of instances in postgres DB cluster"
  default = 1
}

variable "ssl_postgres_protocol" {
  type = string
  description = "minimum ssl protocol version"
  default = "TLSv1.2"
}

variable "postgres_storage_encrypted" {
  type = string
  description = "Postgres DB Encryption-at-rest enablement"
  default = true
}

variable "postgres_port" {
  type = string
  description = "Postgres DB inbound port"
  default = "5432"
}

variable "postgres_retention_period" {
  type = number
  description = "How many days should the backups be kept, default is 1 day"
  default = 7
}

variable "postgres_kms_key_id" {
  type = string
  description = "ARN for AWS KMS Key to encrypt Postgres DB"
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
  default = []
}

variable "ptl_allowed_incoming_cidrs" {
  description = "List of exernal CIDR that will be allowed to service LBs (where needed)"
  type = list(string)
  default = []
}

variable "lb_reserved_ips" {
  type = list(string)
  description = "List of IPs that should be used for load balancer in components - required for async communication"
  default = []
}
