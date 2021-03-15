resource "aws_lb" "service_load_balancer" {
  count = var.enable_load_balancing ? 1 :0
  name = "${replace(local.resource_prefix,"_","-")}-lb"
  internal = true
  load_balancer_type = var.load_balancer_type
  security_groups = local.lb_sgs

  dynamic "subnet_mapping" {
    for_each = local.lb_subnets_to_private_ips
    content {
      subnet_id = subnet_mapping.key
      private_ipv4_address = subnet_mapping.value != "auto" ?  subnet_mapping.value : null
    }
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-lb"
  })
}
