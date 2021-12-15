resource "aws_security_group" "postgres_sg" {
  name = "${local.resource_prefix}-postgres_sg"
  vpc_id = aws_vpc.base_vpc.id
  description = "Security Group for postgres DB in env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-postgres_sg"
  })
}

resource "aws_security_group" "postgres_access_sg" {
  name = "${local.resource_prefix}-postgres_access_sg"
  description = "Security Group that allow access to postgres DB in env: ${var.environment}"
  vpc_id = aws_vpc.base_vpc.id
  
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-postgres_access_sg"
  })
}