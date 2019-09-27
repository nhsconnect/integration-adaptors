#########################
# ElastiCache Resources
#
# Note that data at rest within the ElastiCache cluster created is encrypted using an AWS-owned customer master key.
# This can be changed to an AWS-managed customer master key.
# See https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/at-rest-encryption.html#using-customer-managed-keys-for-elasticache-security
# for more details.
#########################

# The MHS ElastiCache replication group. Defines the ElastiCache cluster. One node is defined for each availability zone
# (see number_cache_clusters).
resource "aws_elasticache_replication_group" "elasticache_replication_group" {
  automatic_failover_enabled = true
  replication_group_id = "${var.environment_id}-rg"
  replication_group_description = "An ElastiCache cluster for the environment: ${var.environment_id}"
  node_type = var.elasticache_node_type
  number_cache_clusters = length(data.aws_availability_zones.all.names)
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  port = 6379
  subnet_group_name = aws_elasticache_subnet_group.elasticache_subnet_group.name
  security_group_ids = [
    aws_security_group.sds_cache_security_group.id
  ]
}

# The MHS ElastiCache subnet group. Defines the subnets that the ElastiCache cluster should place replicas in.
resource "aws_elasticache_subnet_group" "elasticache_subnet_group" {
  name = "${var.environment_id}-elasticache-subnet-group"
  description = "Subnet group for the ElastiCache cluster used in environment: ${var.environment_id}"
  subnet_ids = aws_subnet.mhs_subnet.*.id
}
