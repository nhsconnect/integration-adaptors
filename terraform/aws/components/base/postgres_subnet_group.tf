resource "aws_db_subnet_group" "base_postgres_subnet_group" {
  name =  "${local.resource_prefix}-postgres_subnet_group"
  subnet_ids = aws_subnet.base_subnet.*.id
  description = "RDS DB Subnet Group for env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-postgres_subnet_group"
  })
}