resource "aws_route" "route_all_to_ptl" {
  count = var.ptl_connected ? length(var.ptl_hscn_prefixes) : 0
  route_table_id = aws_route_table.nhs_ptl[0].id
  destination_cidr_block = var.ptl_hscn_prefixes[count.index]
  gateway_id = data.aws_vpn_gateway.ptl_gateway[0].id
}

resource "aws_route" "ptl_internet_route" {
  count = var.ptl_connected && var.enable_internet_access ? length(var.ptl_internet_prefixes) : 0
  route_table_id = aws_route_table.nhs_ptl[0].id
  destination_cidr_block = var.ptl_internet_prefixes[count.index]
   nat_gateway_id = aws_nat_gateway.nat_gw[0].id
}

resource "aws_vpc_endpoint_route_table_association" "s3_vpce_on_ptl_rt" {
  count = var.ptl_connected ? 1 : 0
  route_table_id = aws_route_table.nhs_ptl[0].id
  vpc_endpoint_id = aws_vpc_endpoint.s3_endpoint.id
}

# resource "aws_vpc_endpoint_route_table_association" "dynamodb_vpce_on_ptl_rt" {
#   count = var.ptl_connected ? 1 : 0
#   route_table_id = aws_route_table.nhs_ptl[0].id
#   vpc_endpoint_id = aws_vpc_endpoint.dynamodb_endpoint.id
# }

resource "aws_route" "mq_to_ptl_route" {
  count = var.ptl_connected ? 1 : 0
  route_table_id = data.aws_vpc.mq_vpc.main_route_table_id
  destination_cidr_block = aws_vpc_ipv4_cidr_block_association.base_ptl_cidr[0].cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

resource "aws_route" "ptl_to_mq_route" {
  count = var.ptl_connected ? 1 : 0
  route_table_id = aws_route_table.nhs_ptl[0].id
  destination_cidr_block = data.aws_vpc.mq_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}
