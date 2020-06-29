locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.component}"
  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]
  account_public_cidr = cidrsubnet(aws_vpc.account_vpc.cidr_block,10,0)
  account_private_cidr = [
    cidrsubnet(aws_vpc.account_vpc.cidr_block,10,1),
    cidrsubnet(aws_vpc.account_vpc.cidr_block,10,2),
    cidrsubnet(aws_vpc.account_vpc.cidr_block,10,3)
  ]
}