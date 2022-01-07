resource "aws_security_group" "pss_container_access_sg" {
  name = "${local.resource_prefix}_container_access_sg"
  description = "SG to access pss container in env: ${var.environment}"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}_container_access_sg"
  })
}
