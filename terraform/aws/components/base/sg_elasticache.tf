resource "aws_security_group" "elasticache_sg" {
  name = "${local.resource_prefix}-elasticache_sg"
  vpc_id = aws_vpc.base_vpc.id
  description = "Security Group for ElastiCache(Redis) in env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-elasticache_sg"
  })
}
