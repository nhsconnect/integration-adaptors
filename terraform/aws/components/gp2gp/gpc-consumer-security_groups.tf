resource "aws_security_group" "gpc-consumer_external_access" {
  name = "${local.resource_prefix}-gpc-consumer_access_sg"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-gpc-consumer_access_sg"
  })
  description = "SG for additional gpc-consumer access in env: ${var.environment}"
}