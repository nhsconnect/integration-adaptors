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

# Add a route to the NHAIS VPC in the DLT VPC route table
resource "aws_route" "dlt_to_base_route" {
  route_table_id = data.aws_vpc.dlt_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.dlt_peering.id
  depends_on = [aws_vpc_peering_connection.dlt_peering]
}

# Add route to the NHAIS VPC from the second DLT route table
resource "aws_route" "nhais_to_dlt_route" {
  route_table_id = var.second_dlt_route_id
  destination_cidr_block = aws_vpc.base_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.dlt_peering.id
  depends_on = [aws_vpc_peering_connection.dlt_peering]
}

# Add a route to the DLT VPC in the NHAIS VPC route table
resource "aws_route" "base_to_dlt_route" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = data.aws_vpc.dlt_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.dlt_peering.id
  depends_on = [aws_vpc_peering_connection.dlt_peering]
}
# resource "aws_security_group_rule" "nhais_inbound_security_group_amazon_dlt_ingress_rule" {
#   security_group_id = aws_security_group.core_sg.id
#   type = "ingress"
#   from_port = 80
#   to_port = 80
#   protocol = "tcp"
#   # Not making any assumptions here about the internal structure of the DLT VPC.
#   # This can be changed and made more specific to lock this down more.
#   cidr_blocks = [
#     data.aws_vpc.dlt_vpc.cidr_block]
#   description = "Allow inbound requests to nhais tasks"
# }

# resource "aws_security_group_rule" "nhais_inbound_security_group_amazon_dlt_egress_rule" {
#   security_group_id = aws_security_group.core_sg.id
#   type = "egress"
#   from_port = 80
#   to_port = 80
#   protocol = "tcp"
#   # Not making any assumptions here about the internal structure of the DLT VPC.
#   # This can be changed and made more specific to lock this down more.
#   cidr_blocks = [
#     data.aws_vpc.dlt_vpc.cidr_block]
#   description = "Allow outbound requests to Outbound tasks"
# }
# Allow DNS resolution of the domain names defined in route53.tf in the DLT VPC
resource "aws_route53_zone_association" "DLT_hosted_zone_nhais_vpc_association" {
  zone_id = aws_route53_zone.base_zone.zone_id
  vpc_id = data.aws_vpc.dlt_vpc.id
}
