# vpc peering to the network where DLT is hosted
data "aws_vpc" "dlt_vpc" {
  id = var.dlt_vpc_id
}

resource "aws_vpc_peering_connection" "dlt_peering" {
  vpc_id = aws_vpc.base_vpc.id
  peer_vpc_id = data.aws_vpc.dlt_vpc.id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-dlt-vpc-peering"
  })
}

# Add a route to the MHS VPC in the supplier VPC route table
resource "aws_route" "dlt_to_base_route" {
  route_table_id = data.aws_vpc.dlt_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.dlt_peering.id
  depends_on = [aws_vpc_peering_connection.dlt_peering]
}

# Add a route to the supplier VPC in the MHS VPC route table
resource "aws_route" "base_to_dlt_route" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = data.aws_vpc.dlt_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.dlt_peering.id
  depends_on = [aws_vpc_peering_connection.dlt_peering]
}
resource "aws_security_group_rule" "mhs_inbound_security_group_amazon_dlt_ingress_rule" {
  security_group_id = aws_security_group.core_sg.id
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  # Not making any assumptions here about the internal structure of the supplier VPC.
  # This can be changed and made more specific to lock this down more.
  cidr_blocks = [
    data.aws_vpc.dlt_vpc.cidr_block]
  description = "Allow inbound requests to inbound tasks"
}

resource "aws_security_group_rule" "mhs_inbound_security_group_amazon_dlt_egress_rule" {
  security_group_id = aws_security_group.core_sg.id
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  # Not making any assumptions here about the internal structure of the supplier VPC.
  # This can be changed and made more specific to lock this down more.
  cidr_blocks = [
    data.aws_vpc.dlt_vpc.cidr_block]
  description = "Allow outbound requests to Outbound tasks"
}
