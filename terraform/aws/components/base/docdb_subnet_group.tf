resource "aws_docdb_subnet_group" "base_db_subnet_group" {
  name =  "${local.resource_prefix}-db_subnet_group"
  subnet_ids = aws_subnet.base_subnet.*.id
  description = "Document DB Subnet Group for env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-db_subnet_group"
  })
}