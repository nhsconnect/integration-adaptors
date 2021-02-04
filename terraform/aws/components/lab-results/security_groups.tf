resource "aws_security_group" "lab-results_external_access" {
  name = "${local.resource_prefix}-lab-results_access_sg"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-lab-results_access_sg"
  })
  description = "SG for additional lab-results access in env: ${var.environment}"
}
