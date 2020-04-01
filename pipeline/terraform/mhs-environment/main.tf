##################
# Main Terraform file
#
# - Setup Terraform backend
# - configure AWS provider
# - Setup MHS VPC
# - Setup private subnets
##################

terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    # Intentionally blank - all parameters provided in command line
  }
}

# Setup AWS provider
provider "aws" {
  profile = "default"
  version = "~> 2.27"
  region = var.region
}

# Get the list of availability zones for the selected AWS region
data "aws_availability_zones" "all" {}

# Get details of the supplier VPC the MHS VPC will have a peering connection with
data "aws_vpc" "supplier_vpc" {
  id = var.supplier_vpc_id
}

# The MHS VPC that contains the running MHS
resource "aws_vpc" "mhs_vpc" {
  # Note that this cidr block must not overlap with the cidr blocks of the VPCs
  # that the MHS VPC is peered with.
  cidr_block = var.mhs_vpc_cidr_block
  enable_dns_hostnames = true

  tags = {
    Name = "${var.environment_id}-mhs-vpc"
    EnvironmentId = var.environment_id
  }
}

# Create a private subnet in each availability zone in the region.
resource "aws_subnet" "mhs_subnet" {
  count = length(data.aws_availability_zones.all.names)

  vpc_id = aws_vpc.mhs_vpc.id
  availability_zone = data.aws_availability_zones.all.names[count.index]

  # Generates a CIDR block with a different prefix within the VPC's CIDR block for each subnet being created.
  # E.g if the VPC's CIDR block is 10.0.0.0/16, this generates subnets that have CIDR blocks 10.0.0.0/24, 10.0.1.0/24,
  # etc.
  cidr_block = cidrsubnet(var.mhs_vpc_cidr_block, 8, count.index)

  map_public_ip_on_launch = false

  tags = {
    Name = "${var.environment_id}-mhs-subnet-${data.aws_availability_zones.all.names[count.index]}"
    EnvironmentId = var.environment_id
  }
}
