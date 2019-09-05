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
