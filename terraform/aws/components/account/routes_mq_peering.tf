resource "aws_route" "mq_to_account_route" {
  route_table_id = data.aws_vpc.mq_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.account_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

resource "aws_route" "account_private_to_mq_route" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = data.aws_vpc.mq_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

resource "aws_route" "account_public_to_mq_route" {
  route_table_id = aws_route_table.public.id
  destination_cidr_block = data.aws_vpc.mq_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}
