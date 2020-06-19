# vpc peering to the network where DLT is hosted
data "aws_vpc" "dlt_vpc" {
  count = var.enable_dlt ? 1 :0
  id = var.dlt_vpc_id
}

resource "aws_vpc_peering_connection" "dlt_peering" {
  count = var.enable_dlt ? 1 :0
  vpc_id = aws_vpc.base_vpc.id
  peer_vpc_id = data.aws_vpc.dlt_vpc[0].id
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
