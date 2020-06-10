resource "aws_route_table" "public" {
  count = var.enable_internet_access ? 1 : 0
  vpc_id = aws_vpc.base_vpc.id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-public_rt"
  })
}

resource "aws_route_table_association" "public_route_public_subnet" {
  count = var.enable_internet_access ? 1 : 0
  subnet_id = aws_subnet.nat_gw_subnet.id
  route_table_id = aws_route_table.public.id 
}
