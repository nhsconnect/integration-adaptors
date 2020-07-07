resource "aws_vpc" "base_vpc" {
  cidr_block = var.base_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-vpc"
  })
}

resource "aws_vpc_ipv4_cidr_block_association" "base_ptl_cidr" {
  count = var.ptl_connected ? 1 : 0
  vpc_id = aws_vpc.base_vpc.id
  cidr_block = var.ptl_assigned_cidr
}
