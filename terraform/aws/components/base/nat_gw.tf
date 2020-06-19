resource "aws_eip" "nat_gw_eip" {
  count = var.enable_internet_access ? 1 : 0
  vpc = true
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nat_gw_eip"
  })
}

resource "aws_nat_gateway" "nat_gw" {
  count = var.enable_internet_access ? 1 : 0
  subnet_id = aws_subnet.public_subnet.id
  allocation_id = aws_eip.nat_gw_eip[0].id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nat_gw_eip"
  })
}
