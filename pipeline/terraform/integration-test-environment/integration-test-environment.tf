provider "aws" {
  profile = "default"
  region = var.region
}

data "aws_availability_zones" "all" {}


resource "aws_vpc" "mhs_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "${var.build_id}-vpc"
    BuildId = var.build_id
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
    Name = "${var.build_id}-mhs-subnet-${count.index}"
    BuildId = var.build_id
  }
}

resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.build_id}-mhs-cluster"

  tags = {
    Name = "${var.build_id}-mhs-cluster"
    BuildId = var.build_id
  }
}
