# general private subnet for things in base component
resource "aws_subnet" "base_subnet" {
  count = length(local.availability_zones)
  vpc_id = aws_vpc.base_vpc.id
  cidr_block = local.base_private_cidr[count.index]
  availability_zone = local.availability_zones[count.index]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-subnet-${count.index}"
  })
}
