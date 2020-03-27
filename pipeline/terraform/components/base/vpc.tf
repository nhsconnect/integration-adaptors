# Get details of the supplier VPC the MHS VPC will have a peering connection with
data "aws_vpc" "supplier_vpc" {
  id = var.supplier_vpc_id
}

# Get details of the Opentest VPC the MHS VPC will have a peering connection with
data "aws_vpc" "opentest_vpc" {
  id = var.opentest_vpc_id
}

# The MHS VPC that contains the running MHS
resource "aws_vpc" "base_vpc" {
  # Note that this cidr block must not overlap with the cidr blocks of the VPCs
  # that the MHS VPC is peered with.
  cidr_block = var.mhs_vpc_cidr_block
  enable_dns_hostnames = true

  tags = {
    Name = "${var.environment_id}-base-vpc"
    EnvironmentId = var.environment_id
  }
}