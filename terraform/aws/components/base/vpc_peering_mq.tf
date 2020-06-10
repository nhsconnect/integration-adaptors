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
