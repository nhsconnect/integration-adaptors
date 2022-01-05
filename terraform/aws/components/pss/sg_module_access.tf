resource "aws_security_group" "pss_external_access" {
  name = "${local.resource_prefix}-external_access_sg"
  description = "SG for additional pss access in env: ${var.environment}"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-external_access_sg"
  })
}
