locals {
  base_public_cidr = cidrsubnet(aws_vpc.base_vpc.cidr_block,10,0)
  base_private_cidr = [
    cidrsubnet(aws_vpc.base_vpc.cidr_block,10,1),
    cidrsubnet(aws_vpc.base_vpc.cidr_block,10,2),
    cidrsubnet(aws_vpc.base_vpc.cidr_block,10,3)
  ]

  nhais_cidr     = cidrsubnet(aws_vpc.base_vpc.cidr_block,8,1)
  OneOneOne_cidr = cidrsubnet(aws_vpc.base_vpc.cidr_block,8,2)
  scr_cidr       = cidrsubnet(aws_vpc.base_vpc.cidr_block,8,3)
  mhs_cidr       = cidrsubnet(aws_vpc.base_vpc.cidr_block,8,4)
  gp2gp_cidr     = cidrsubnet(aws_vpc.base_vpc.cidr_block,8,5)
}

# Guidance on subnets:
# The main subnet is 10.x.0.0/16

# base componenent needs 4 subnets for
# - public subnet - directly connected to Internet Gateway
# - 3 private subnets, for document DB

# each with mask /26
# cidrsubnet("10.x.0.0/16",10,0) - 10.x.0.0/26   public
# cidrsubnet("10.x.0.0/16",10,1) - 10.x.0.64/26  private a
# cidrsubnet("10.x.0.0/16",10,2) - 10.x.0.128/26 private b
# cidrsubnet("10.x.0.0/16",10,3) - 10.x.0.192/26 private c

# together cidrsubnet("10.x.0.0/16",8,0) - 10.x.0.0/24 - for the vpc

# subnets for NHAIS component:

# NHAIS = 10.x.1.0/24
# cidrsubnet("10.x.0.0/16",8,1)
# subnets:
# cidrsubnet("10.x.1.0/24",2,0) - 10.x.0.0/26   - a
# cidrsubnet("10.x.1.0/24",2,1) - 10.x.0.64/26  - b
# cidrsubnet("10.x.1.0/24",2,2) - 10.x.1.128/26 - c
# cidrsubnet("10.x.1.0/24",2,3) - 10.x.0.192/26 reserve not alocated

# 111 = 10.x.2.0/24
# SCR = 10.x.3.0/24 etc
