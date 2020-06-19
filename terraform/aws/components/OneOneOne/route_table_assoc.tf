resource "aws_route_table_association" "private_route_base_subnet" {
  count = length(local.availability_zones)
  subnet_id = aws_subnet.service_subnet[count.index].id
  route_table_id = data.terraform_remote_state.base.outputs.private_nat_gw_route_table
}