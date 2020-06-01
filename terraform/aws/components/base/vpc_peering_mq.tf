# vpc peering to the network where MQ is hosted
data "aws_vpc" "mq_vpc" {
  id = var.mq_vpc_id
}

resource "aws_vpc_peering_connection" "mq_peering" {
  vpc_id = aws_vpc.base_vpc.id
  peer_vpc_id = data.aws_vpc.mq_vpc.id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-mq-vpc-peering"
  })
}

# Add a route to the MHS VPC in the supplier VPC route table
resource "aws_route" "mq_to_base_route" {
  route_table_id = data.aws_vpc.mq_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

# Add a route to the supplier VPC in the MHS VPC route table
resource "aws_route" "base_to_mq_route" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = data.aws_vpc.mq_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.mq_peering.id
  depends_on = [aws_vpc_peering_connection.mq_peering]
}

resource "aws_security_group_rule" "mhs_inbound_security_group_amazon_mq_egress_rule" {
  security_group_id = aws_security_group.core_sg.id
  type = "egress"
  from_port = 5671
  to_port = 5671
  protocol = "tcp"
  # Not making any assumptions here about the internal structure of the supplier VPC.
  # This can be changed and made more specific to lock this down more.
  cidr_blocks = [
    data.aws_vpc.mq_vpc.cidr_block]
  description = "Allow outbound requests to Amazon MQ inbound queue"
}
