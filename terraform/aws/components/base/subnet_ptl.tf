# PTL - separate subnets for LB and others

resource "aws_subnet" "service_containers_subnet" {
  count = var.ptl_connected ? length(local.availability_zones) : 0
  vpc_id  = aws_vpc_ipv4_cidr_block_association.base_ptl_cidr[0].vpc_id
  cidr_block = local.ptl_containers_subnet_cidrs[count.index]
  availability_zone = local.availability_zones[count.index]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-ptl_containers_subnet-${count.index}"
  })
}

resource "aws_subnet" "service_lb_subnet" {
  count = var.ptl_connected ? length(local.ptl_lb_availability_zones) : 0
  vpc_id  = aws_vpc_ipv4_cidr_block_association.base_ptl_cidr[0].vpc_id
  cidr_block = local.ptl_lb_subnet_cidrs[count.index]
  availability_zone = local.ptl_lb_availability_zones[count.index]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-ptl_lb_subnet-${count.index}"
  })
}
