data "aws_vpc" "supplier_vpc" {
  id = var.supplier_vpc_id
}

resource "aws_vpc_peering_connection" "supplier_peering_connection" {
  peer_vpc_id = var.supplier_vpc_id
  vpc_id = aws_vpc.mhs_vpc.id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = {
    Name = "${var.environment_id}-mhs-supplier-peering-connection"
    EnvironmentId = var.environment_id
  }
}

resource "aws_route" "supplier_to_mhs_route" {
  route_table_id = data.aws_vpc.supplier_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.mhs_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.supplier_peering_connection.id
}

resource "aws_route" "mhs_to_supplier_route" {
  route_table_id = aws_vpc.mhs_vpc.main_route_table_id
  destination_cidr_block = data.aws_vpc.supplier_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.supplier_peering_connection.id
}

resource "aws_route53_zone_association" "supplier_hosted_zone_mhs_vpc_association" {
  zone_id = aws_route53_zone.mhs_hosted_zone.zone_id
  vpc_id  = data.aws_vpc.supplier_vpc.id
}


data "aws_vpc" "opentest_vpc" {
  id = var.opentest_vpc_id
}

resource "aws_vpc_peering_connection" "opentest_peering_connection" {
  peer_vpc_id = var.opentest_vpc_id
  vpc_id = aws_vpc.mhs_vpc.id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = {
    Name = "${var.environment_id}-mhs-opentest-peering-connection"
    EnvironmentId = var.environment_id
  }
}

resource "aws_route" "mhs_to_opentest_route" {
  route_table_id = aws_vpc.mhs_vpc.main_route_table_id
  destination_cidr_block = data.aws_vpc.opentest_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.opentest_peering_connection.id
}

resource "aws_route" "opentest_to_mhs_route" {
  route_table_id = data.aws_vpc.opentest_vpc.main_route_table_id
  destination_cidr_block = aws_vpc.mhs_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.opentest_peering_connection.id
}

resource "aws_route53_zone_association" "opentest_hosted_zone_mhs_vpc_association" {
  zone_id = aws_route53_zone.mhs_hosted_zone.zone_id
  vpc_id  = data.aws_vpc.opentest_vpc.id
}

resource "aws_security_group_rule" "mhs_outbound_security_group_opentest_http_proxy_egress_rule" {
  security_group_id = aws_security_group.mhs_outbound_security_group.id
  type = "egress"
  from_port = 3128
  to_port = 3128
  protocol = "tcp"
  cidr_blocks = [data.aws_vpc.opentest_vpc.cidr_block]
  description = "HTTP proxy to Opentest"
}

resource "aws_security_group_rule" "mhs_route_security_group_opentest_ldap_proxy_egress_rule" {
  security_group_id = aws_security_group.mhs_route_security_group.id
  type = "egress"
  from_port = 389
  to_port = 389
  protocol = "tcp"
  cidr_blocks = [data.aws_vpc.opentest_vpc.cidr_block]
  description = "HTTP proxy to Opentest"
}
