variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "environment_id" {
  type = string
  description = "An ID used to identify the environment being deployed by this configuration. As this is used as a prefix for the names of most resources this should be kept to 20 characters or less."
}

variable "build_id" {
  type = string
  description = "ID used to identify the current build."
}

variable "mhs_vpc_cidr_block" {
  type = string
  description = "The CIDR block to use for the MHS VPC that is created. Should be a /16 block. Note that this cidr block must not overlap with the cidr blocks of the VPCs that the MHS VPC is to be peered with."
  default = "10.0.0.0/16"
}

variable "supplier_vpc_id" {
  type = string
  description = "VPC id of the supplier system that connects to the MHS"
}
variable "opentest_vpc_id" {
  type = string
  description = "VPC id of the VPC that contains the Opentest connection to Spine"
}

variable "internal_root_domain" {
  type = string
  description = "Domain name to be used internally to refer to parts of the MHS (subdomains will be created off of this root domain). This domain name should not clash with any domain name on the internet. e.g. internal.somedomainyoucontrol.com"
}

variable "mhs_outbound_service_minimum_instance_count" {
  type = number
  description = "The minimum number of instances of MHS outbound to run. This will be the number of instances deployed initially."
}

variable "mhs_outbound_service_maximum_instance_count" {
  type = number
  description = "The maximum number of instances of MHS outbound to run."
}

variable "mhs_outbound_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an MHS outbound service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "mhs_inbound_service_minimum_instance_count" {
  type = number
  description = "The minimum number of instances of MHS inbound to run. This will be the number of instances deployed initially."
}

variable "mhs_inbound_service_maximum_instance_count" {
  type = number
  description = "The maximum number of instances of MHS inbound to run."
}

variable "mhs_inbound_service_target_cpu_utilization" {
  type = number
  description = "The target CPU utilization (in percent) that an MHS inbound service should have. The number of services will be autoscaled so each instance achieves this level of utilization. This value should be tuned based on the results of performance testing."
  default = 80
}

variable "mhs_route_service_minimum_instance_count" {
  type = number
  description = "The minimum number of instances of MHS route service to run. This will be the number of instances deployed initially."
}

variable "mhs_route_service_maximum_instance_count" {
  type = number
  description = "The maximum number of instances of MHS route service to run."
}

variable "mhs_route_service_target_request_count" {
  type = number
  description = "The target number of requests per minute that an MHS route service should handle. The number of services will be autoscaled so each instance handles this number of requests. This value should be tuned based on the results of performance testing."
  default = 1200
}

variable "task_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to use other AWS services."
}

variable "execution_role_arn" {
  type = string
  description = "ARN of the IAM role for MHS containers to pull from ECR and put logs in Cloudwatch."
}

variable "task_scaling_role_arn" {
  type = string
  description = "ARN of the IAM role for ECS to use when auto-scaling services"
}

variable "ecr_address" {
  type = string
  description = "Address of the ECR registry to get containers from."
}

variable "mhs_log_level" {
  type = string
  description = "Log level for the MHS application."
}

variable "mhs_resynchroniser_max_retries" {
  type = string
  description = "The number of retry attempts to the sync-async state store that should be made whilst attempting to resynchronise a sync-async message"
}

variable "mhs_resynchroniser_interval" {
  type = string
  description = "Time between calls to the sync-async store during resynchronisation"
}

variable "mhs_outbound_http_proxy" {
  type = string
  description = "Address of the HTTP proxy to proxy downstream requests from MHS outbound."
  default = ""
}

variable "mhs_outbound_validate_certificate" {
  type = string
  description = "Verification of the server certificate received when making a connection to the spine MHS"
  default = "true"
}

variable "mhs_state_table_read_capacity" {
  type = number
  description = "Read capacity of the DynamoDB state table used by the MHS application."
}

variable "mhs_state_table_write_capacity" {
  type = number
  description = "Write capacity of the DynamoDB state table used by the MHS application."
}

variable "mhs_sync_async_table_read_capacity" {
  type = number
  description = "Read capacity of the DynamoDB sync-async table used by the MHS application."
}

variable "mhs_sync_async_table_write_capacity" {
  type = number
  description = "Write capacity of the DynamoDB sync-async table used by the MHS application."
}

variable "mhs_spine_org_code" {
  type = string
  description = "The organisation code for the Spine instance that your MHS is communicating with."
}

variable "inbound_queue_brokers" {
  type = string
  description = "URL(s) of the Amazon MQ AMQP inbound queues to connect to."
}

variable "inbound_queue_name" {
  type = string
  description = "Name of the inbound queue"
}

variable "inbound_queue_username_arn" {
  type = string
  description = "ARN of the secrets manager secret of the username to use when connecting to the inbound queue."
}

variable "inbound_queue_password_arn" {
  type = string
  description = "ARN of the secrets manager secret of the password to use when connecting to the inbound queue."
}

variable "party_key_arn" {
  type = string
  description = "ARN of the secrets manager secret of the party key associated with the MHS."
}

variable "client_cert_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint certificate."
}

variable "client_key_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint private key."
}

variable "ca_certs_arn" {
  type = string
  description = "ARN of the secrets manager secret of the endpoint issuing subCA certificate and root CA Certificate (in that order)."
}

variable "route_ca_certs_arn" {
  type = string
  description = "ARN of the secrets manager secret containing the CA certificates to be used to verify the certificate presented by the Spine Route Lookup service. Required if you are using certificates that are not signed by a legitimate CA."
  default = ""
}

variable "outbound_alb_certificate_arn" {
  type = string
  description = "ARN of the TLS certificate that the outbound load balancer should present. This can be a certificate stored in IAM or ACM."
}

variable "route_alb_certificate_arn" {
  type = string
  description = "ARN of the TLS certificate that the outbound load balancer should present. This can be a certificate stored in IAM or ACM."
}

variable "spineroutelookup_service_sds_url" {
  type = string
  description = "The SDS URL the Spine Route Lookup service should communicate with."
}

variable "spineroutelookup_service_search_base" {
  type = string
  description = "The LDAP location the Spine Route Lookup service should use as the base of its searches when querying SDS."
}

variable "spineroutelookup_service_disable_sds_tls" {
  type = string
  description = "Whether TLS should be disabled for connections to SDS."
  default = "False"
}

variable "elasticache_node_type" {
  type = string
  description = "The type of ElastiCache node to use when deploying the ElastiCache cluster. Possible node types can be found from https://aws.amazon.com/elasticache/features/#Available_Cache_Node_Types"
}

variable "mhs_resync_initial_delay" {
  type = number
  description = "The delay before the first poll to the sync async store after receiving an acknowledgement from Spine"
  default = 0.150
}

variable "mhs_spine_request_max_size" {
  type = number
  description = "The maximum size of the request body (in bytes) that MHS outbound sends to Spine. This should be set minus any HTTP headers and other content in the HTTP packets sent to Spine."
  default = 4999600 # This is 5 000 000 - 400 ie 5MB - 400 bytes, roughly the size of the rest of the HTTP packet
}

variable "mhs_forward_reliable_endpoint_url" {
  type = string
  description = "The URL to communicate with Spine for Forward Reliable messaging from the outbound service"
}

variable "lb_deregistration_delay" {
  type = number
  default = 40
  description = "How long the LB should wait before removing deregistered members, AWS default is 300 seconds"
}

variable "healthcheck_threshold" {
  type = number
  default = 3
  description = "Retries for confirming target status - healthy or unhealthy, AWS default is 3"
}
