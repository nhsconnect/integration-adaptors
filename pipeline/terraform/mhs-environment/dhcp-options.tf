resource "aws_vpc_dhcp_options" "nhs_dhcp_options" {
  domain_name = "nhs.uk"
  domain_name_servers = ["155.231.231.1", "155.231.231.2"]
}

resource "aws_vpc_dhcp_options" "aws_dhcp_options" { 
  domain_name = "${var.region}-compute.internal"
  domain_name_servers = ["AmazonProvidedDNS"]
}

resource "aws_vpc_dhcp_options_association" "nhs_association" {
  count = var.dhcp_options_in_use == "nhs" ? 1 : 0
  vpc_id = aws_vpc.mhs_vpc.id
  dhcp_options_id = aws_vpc_dhcp_options.nhs_dhcp_options.id
}

resource "aws_vpc_dhcp_options_association" "aws_association" {
  count = var.dhcp_options_in_use == "aws" ? 1: 0
  vpc_id = aws_vpc.mhs_vpc.id
  dhcp_options_id = aws_vpc_dhcp_options.aws_dhcp_options.id
} 