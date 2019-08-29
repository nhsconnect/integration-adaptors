provider "aws" {
  profile = "default"
  region = var.region
}

resource "aws_vpc" "mhs_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "${var.build_id}-vpc"
  }
}
