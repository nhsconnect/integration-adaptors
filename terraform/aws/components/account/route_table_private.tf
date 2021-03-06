resource "aws_route_table" "private" {
  vpc_id = aws_vpc.account_vpc.id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-private_rt"
  })
}

resource "aws_route_table_association" "private_route_base_subnet" {
  count  = length(local.availability_zones)
  subnet_id = aws_subnet.account_subnet[count.index].id
  route_table_id = aws_route_table.private.id
}
