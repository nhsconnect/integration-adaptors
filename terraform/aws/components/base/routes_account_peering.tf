resource "aws_route" "account_to_base_route" {
  route_table_id = data.terraform_remote_state.account.outputs.account_vpc_route_table_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.account_peering.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}

resource "aws_route" "base_to_account_route" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = data.terraform_remote_state.account.outputs.account_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.account_peering.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}

resource "aws_route" "account_public_to_base" {
  route_table_id = data.terraform_remote_state.account.outputs.account_public_route_table_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.account_peering.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}

# For PTL subnets

resource "aws_route" "account_public_to_base_ptl" {
  count = var.ptl_connected ? 1 : 0
  route_table_id = data.terraform_remote_state.account.outputs.account_public_route_table_id
  destination_cidr_block = aws_vpc_ipv4_cidr_block_association.base_ptl_cidr[0].cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.account_peering.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}

resource "aws_route" "base_ptl_to_account_public_route" {
  count = var.ptl_connected ? 1 : 0
  route_table_id = aws_route_table.nhs_ptl[0].id
  destination_cidr_block = data.terraform_remote_state.account.outputs.account_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.account_peering.id
  depends_on = [aws_vpc_peering_connection.account_peering]
}
