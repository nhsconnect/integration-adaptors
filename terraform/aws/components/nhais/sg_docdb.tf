resource "aws_security_group" "docdb_sg" {
  name = "${local.resource_prefix}-docdb_sg"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  description = "Security Group for DocDB in env: ${var.environment}"

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-docdb_sg"
  })
}

resource "aws_security_group" "docdb_access_sg" {
  name = "${local.resource_prefix}-docdb_access_sg"
  description = "Security Group that allow access to DocDB in env: ${var.environment}"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-docdb_access_sg"
  })
}