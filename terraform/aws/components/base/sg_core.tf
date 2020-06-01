# Security group for core services like VPC Endpoints
resource "aws_security_group" "core_sg" { 
  name = "${local.resource_prefix}-core_sg"
  description = "Security group that allows access to core services in env: ${var.environment}"
  vpc_id = aws_vpc.base_vpc.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-core_sg"
  })
}