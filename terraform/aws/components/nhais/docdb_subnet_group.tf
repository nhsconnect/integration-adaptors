resource "aws_docdb_subnet_group" "nhais_db_subnet_group" {
  name =  "${local.resource_prefix}-db_subnet_group"
  subnet_ids = aws_subnet.service_subnet.*.id
  description = "Document DB Subnet Group for env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-db_subnet_group"
  })
}