resource "aws_route_table" "public" { 
  vpc_id = aws_vpc.base_vpc.id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-public_rt"
  })
}

resource "aws_route_table_association" "public_route_public_subnet" {
  subnet_id = aws_subnet.nat_gw_subnet.id
  route_table_id = aws_route_table.public.id 
}

