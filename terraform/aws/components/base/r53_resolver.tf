resource "aws_route53_resolver_endpoint" "nhs_resolver" {
  count = var.ptl_connected ? 1 : 0
  name = "${local.resource_prefix}-r53_resolver"
  direction = "OUTBOUND"

  security_group_ids = [
    aws_security_group.r53_resolver_sg[0].id,
  ]

  # TODO change to dynamic - although tricky
  ip_address {
    subnet_id = aws_subnet.service_containers_subnet[0].id
  }

  ip_address {
    subnet_id = aws_subnet.service_containers_subnet[1].id
  }

  ip_address {
    subnet_id = aws_subnet.service_containers_subnet[2].id
  }

  # ip_address {
  #   subnet_id = aws_subnet.service_lb_subnet[0].id
  # }

  # ip_address {
  #   subnet_id = aws_subnet.service_lb_subnet[1].id
  # }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-r53_resolver"
  })
}

resource "aws_route53_resolver_rule" "nhs_dns_resolver_rule" {
  count = var.ptl_connected ? 1 : 0
  rule_type = "FORWARD"
  domain_name = "nhs.uk"
  name = "${local.resource_prefix}-r53_resolver_rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.nhs_resolver[0].id

  target_ip {
    ip = var.ptl_dns_servers[0]
  }

  target_ip {
    ip = var.ptl_dns_servers[1]
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-r53_resolver_rule"
  })
}

resource "aws_route53_resolver_rule_association" "resolver_to_vpc_assoc" {
  count = var.ptl_connected ? 1 : 0
  resolver_rule_id =  aws_route53_resolver_rule.nhs_dns_resolver_rule[0].id
  vpc_id = aws_vpc.base_vpc.id
}
