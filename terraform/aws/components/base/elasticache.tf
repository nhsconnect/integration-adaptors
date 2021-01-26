resource "aws_elasticache_replication_group" "elasticache_replication_group" {
  automatic_failover_enabled = true
  replication_group_id = "${local.resource_prefix}-ec-rg"
  replication_group_description = "An ElastiCache cluster for the environment: ${var.environment}"
  node_type = var.elasticache_node_type
  number_cache_clusters = length(local.availability_zones)
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  engine = "redis"
  port = 6379
  subnet_group_name = aws_elasticache_subnet_group.elasticache_subnet_group.name
  security_group_ids = [
    aws_security_group.elasticache_sg.id
  ]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-elasticache-replication_group"
  })
}

# The MHS ElastiCache subnet group. Defines the subnets that the ElastiCache cluster should place replicas in.
resource "aws_elasticache_subnet_group" "elasticache_subnet_group" {
  name =  "${local.resource_prefix}-ec-subnet-group"
  description = "Subnet group for the ElastiCache cluster used in environment: ${var.environment}"
  subnet_ids = aws_subnet.base_subnet.*.id
}
