resource "aws_security_group" "nhais-responder_external_access" {
  name = "${local.resource_prefix}-nhais-responder_access_sg"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nhais-responder_access_sg"
  })
  description = "SG for additional nhais-responder access in env: ${var.environment}"
}