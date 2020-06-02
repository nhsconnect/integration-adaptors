resource "aws_eip" "nat_gw_eip" {
  vpc = true
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nat_gw_eip"
  })
}

resource "aws_nat_gateway" "nat_gw" {
  subnet_id = aws_subnet.nat_gw_subnet.id
  allocation_id = aws_eip.nat_gw_eip.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nat_gw_eip"
  })
}
