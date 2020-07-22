resource "aws_vpn_gateway_attachment" "ptl_vpn_gw_attachment" {
  count = var.ptl_connected ? 1 : 0
  vpc_id = aws_vpc.base_vpc.id
  vpn_gateway_id = data.aws_vpn_gateway.ptl_gateway[0].id
}
