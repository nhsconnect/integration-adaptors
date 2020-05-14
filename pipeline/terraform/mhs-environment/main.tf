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

# The minimal size for aws subnet is /28 - 14 hosts
# We need at least two of these for inbound load balancer
# We have to make sure that the assigned ip is always available to the Inbound Load Balancer
# For Inbound LB
# cidrsubnet("10.239.66.128/25",3,0) # 10.239.66.128/28 # zone a
# cidrsubnet("10.239.66.128/25",3,1) # 10.239.66.144/28 # zone b
# For everything else
# cidrsubnet("10.239.66.128/25",2,1) # 10.239.66.160/27 # zone a
# cidrsubnet("10.239.66.128/25",2,2) # 10.239.66.192/27 # zone b
# cidrsubnet("10.239.66.128/25",2,3) # 10.239.66.224/27 # zone c


# Create a private subnet in each availability zone in the region.
resource "aws_subnet" "mhs_subnet" {
  count = length(data.aws_availability_zones.all.names)
  vpc_id = aws_vpc.mhs_vpc.id
  availability_zone = data.aws_availability_zones.all.names[count.index]

  # Generates a CIDR block with a different prefix within the VPC's CIDR block for each subnet being created.
  # E.g if the VPC's CIDR block is 10.0.0.0/16, this generates subnets that have CIDR blocks 10.0.0.0/24, 10.0.1.0/24,
  # etc.
  cidr_block = cidrsubnet(var.mhs_vpc_cidr_block, 2, count.index + 1)

  map_public_ip_on_launch = false

  tags = {
    Name = "${var.environment_id}-mhs-subnet-${data.aws_availability_zones.all.names[count.index]}"
    EnvironmentId = var.environment_id
  }
}

resource "aws_subnet" "inbound_lb_subnet" {
  count = 2
  vpc_id = aws_vpc.mhs_vpc.id
  availability_zone = data.aws_availability_zones.all.names[count.index]
  cidr_block = cidrsubnet(var.mhs_vpc_cidr_block, 3, count.index)

  map_public_ip_on_launch = false

  tags = {
    Name = "${var.environment_id}-mhs-inbound-lb-subnet-${data.aws_availability_zones.all.names[count.index]}"
    EnvironmentId = var.environment_id
  }
}