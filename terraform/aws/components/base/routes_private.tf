resource "aws_route" "route_private_to_nat_gw" {
  count = var.enable_internet_access ? 1 : 0
  route_table_id = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = aws_nat_gateway.nat_gw.id
}

resource "aws_vpc_endpoint_route_table_association" "s3_vpce_on_private_rt" {
  route_table_id = aws_route_table.private.id
  vpc_endpoint_id = aws_vpc_endpoint.s3_endpoint.id
}

resource "aws_vpc_endpoint_route_table_association" "dynamodb_vpce_on_private_rt" {
  route_table_id = aws_route_table.private.id
  vpc_endpoint_id = aws_vpc_endpoint.dynamodb_endpoint.id
}