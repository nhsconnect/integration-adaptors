resource "aws_vpc_dhcp_options" "aws_dhcp_options" {
  domain_name = "${var.region}-compute.internal"
  domain_name_servers = ["AmazonProvidedDNS"]

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-aws_dhcp_options"
  })
}

resource "aws_vpc_dhcp_options_association" "aws_dhcp_association" {
  #count = var.ptl_connected ? 0 : 1
  vpc_id = aws_vpc.base_vpc.id
  dhcp_options_id = aws_vpc_dhcp_options.aws_dhcp_options.id
}

# resource "aws_vpc_dhcp_options" "nhs_dhcp_options" {
#   count = var.ptl_connected ? 1 : 0
#   domain_name = "nhs.uk"
#   domain_name_servers = [var.ptl_dns_servers[0], "AmazonProvidedDNS"]

#   tags = merge(local.default_tags,{
#     Name = "${local.resource_prefix}-nhs_dhcp_options"
#   })
# }

# resource "aws_vpc_dhcp_options_association" "nhs_dhcp_association" {
#   count = var.ptl_connected ? 1 : 0
#   vpc_id = aws_vpc.base_vpc.id
#   dhcp_options_id = aws_vpc_dhcp_options.nhs_dhcp_options[0].id
# }
