resource "aws_security_group" "pss_testbox_sg" {
  name = "${local.resource_prefix}_testbox_sg"
  description = "SG for controlling in and out of pss testbox"
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}_testbox_sg"
  })
}