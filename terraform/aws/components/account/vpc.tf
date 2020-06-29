resource "aws_vpc" "account_vpc" {
  cidr_block = var.account_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-vpc"
  })
}
