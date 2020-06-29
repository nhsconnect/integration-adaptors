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
