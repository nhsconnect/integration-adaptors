# vpc peering to the account component
resource "aws_vpc_peering_connection" "account_peering" {
  vpc_id = aws_vpc.base_vpc.id
  peer_vpc_id = data.terraform_remote_state.account.outputs.account_vpc_id
  auto_accept = true

  accepter {
    allow_remote_vpc_dns_resolution = true
  }

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-account-vpc-peering"
  })
}
