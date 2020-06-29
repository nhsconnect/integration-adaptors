resource "aws_security_group" "jumpbox_sg" {
  name = "${local.resource_prefix}-jumpbox_sg"
  description = "SG for controlling in and out of Accounts Jumpbox"
  vpc_id = aws_vpc.account_vpc.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-jumpbox_sg"
  })
}