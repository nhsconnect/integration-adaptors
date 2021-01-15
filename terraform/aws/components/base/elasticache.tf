resource "aws_elasticache_replication_group" "elasticache_replication_group" {
  automatic_failover_enabled = true
  replication_group_id = "${local.resource_prefix}-ec_rg"
  replication_group_description = "An ElastiCache cluster for the environment: ${var.environment}"
  node_type = var.elasticache_node_type
  number_cache_clusters = length(data.aws_availability_zones.all.names)
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
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
  name =  "${local.resource_prefix}-ec_subnet_group"
  description = "Subnet group for the ElastiCache cluster used in environment: ${var.environment}"
  subnet_ids = aws_subnet.base_subnet.*.id
}

resource "aws_security_group" "elasticache_sg" {
  name = "${local.resource_prefix}-elasticache_sg"
  vpc_id = aws_vpc.base_vpc.id
  description = "Security Group for ElastiCache(Redis) in env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-elasticache_sg"
  })
}

resource "aws_security_group_rule" "allow_ingress_in_ec" {
  type = "ingress"
  from_port = aws_elasticache_replication_group.elasticache_replication_group.port
  to_port = aws_elasticache_replication_group.elasticache_replication_group.port
  protocol = "tcp"
  security_group_id = aws_security_group.elasticache_sg.id
  source_security_group_id = aws_security_group.core_sg.id
  description = "Allow incoming from application to Redis in env: ${var.environment}"
}

resource "aws_security_group_rule" "allow_egress_to_ec" {
  type = "egress"
  from_port = aws_elasticache_replication_group.elasticache_replication_group.port
  to_port = aws_elasticache_replication_group.elasticache_replication_group.port
  protocol = "tcp"
  security_group_id = aws_security_group.elasticache_sg.id
  source_security_group_id = aws_security_group.core_sg.id
  description = "Allow outgoing from application to Redis in env: ${var.environment}"
}

output "redis_host" {
  value = aws_elasticache_replication_group.elasticache_replication_group.primary_endpoint_address
}

output redis_port {
  value = aws_elasticache_replication_group.elasticache_replication_group.port
}
