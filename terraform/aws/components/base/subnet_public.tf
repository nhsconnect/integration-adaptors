resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.base_vpc.id
  cidr_block = local.base_public_cidr

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-public_subnet"
  })
}