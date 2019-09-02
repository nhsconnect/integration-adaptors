terraform {
  backend "s3" {
  }
}

provider "aws" {
  profile = "default"
  region = var.region
}

data "aws_availability_zones" "all" {}

resource "aws_vpc" "mhs_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "${var.environment_id}-vpc"
    EnvironmentId = var.environment_id
  }
}

# Create a subnet in each availability zone in the region.
resource "aws_subnet" "mhs_subnet" {
  count = length(data.aws_availability_zones.all.names)

  vpc_id = aws_vpc.mhs_vpc.id
  availability_zone = data.aws_availability_zones.all.names[count.index]
  cidr_block = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.environment_id}-mhs-subnet-${data.aws_availability_zones.all.names[count.index]}"
    EnvironmentId = var.environment_id
  }
}

resource "aws_internet_gateway" "mhs_igw" {
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-mhs-igw"
    EnvironmentId = var.environment_id
  }
}
