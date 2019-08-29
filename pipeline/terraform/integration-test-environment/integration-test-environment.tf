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

resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.build_id}-mhs-cluster"

  tags = {
        "BuildId" = "${var.build_id}"
    }
}
