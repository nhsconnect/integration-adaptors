resource "aws_route_table" "nhs_ptl" {
  count = var.ptl_connected ? 1 : 0
  vpc_id = aws_vpc.base_vpc.id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nhs_ptl_rt"
  })
}

resource "aws_route_table_association" "ptl_container_route_ptl_subnet" {
  count = var.ptl_connected ? length(local.ptl_lb_availability_zones) : 0
  subnet_id = aws_subnet.service_containers_subnet[count.index].id
  route_table_id = aws_route_table.nhs_ptl[0].id 
}

resource "aws_route_table_association" "ptl_lb_route_ptl_subnet" {
  count = var.ptl_connected ? length(local.ptl_lb_availability_zones) : 0
  subnet_id = aws_subnet.service_lb_subnet[count.index].id
  route_table_id = aws_route_table.nhs_ptl[0].id 
}
