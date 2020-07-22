data "aws_vpn_gateway" "ptl_gateway" {
  count = var.ptl_connected ? 1 : 0
  id = var.ptl_vpn_gateway_id
}
