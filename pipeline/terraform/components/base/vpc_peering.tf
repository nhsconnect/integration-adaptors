# VPC peering connection
resource "aws_vpc_peering_connection" "opentest_peering_connection" {
  peer_vpc_id = var.opentest_vpc_id
  vpc_id = aws_vpc.base.id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = {
    Name = "${var.environment_id}-opentest-peering-connection"
    EnvironmentId = var.environment_id
  }
}