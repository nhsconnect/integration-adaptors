resource "aws_route53_resolver_endpoint" "nhs_resolver" {
  name = "${var.environment_id}-nhs_dns_resolver"
  direction = "OUTBOUND"

  security_group_ids = [
    aws_security_group.mhs_route_security_group.id,
    aws_security_group.mhs_outbound_security_group.id,
    "sg-03b13ed465a7f32ca"
  ]
  # Last one is PTL private SG - for the private EC2 Instance

  ip_address {
    subnet_id = aws_subnet.mhs_subnet[0].id
  }

  ip_address {
    subnet_id = aws_subnet.mhs_subnet[1].id
  }

  ip_address {
    subnet_id = aws_subnet.mhs_subnet[2].id
  }

  tags = {
    EnvironmentId = var.environment_id
  }
}

resource "aws_route53_resolver_rule" "nhs_dns_resolver_rule" { 
  rule_type = "FORWARD"
  domain_name = "nhs.uk"
  name = "${var.environment_id}-nhs_dns_resolver_rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.nhs_resolver.id

  target_ip {
    ip = "155.231.231.1"
  }

  target_ip {
    ip = "155.231.231.2"
  }

  tags = {
    EnvironmentId = var.environment_id
  }
}

resource "aws_route53_resolver_rule_association" "resolver_to_vpc_assoc" {
  resolver_rule_id =  aws_route53_resolver_rule.nhs_dns_resolver_rule.id
  vpc_id = aws_vpc.mhs_vpc.id
  name = "${var.environment_id}-nhs_dns_resolver_rule_assoc"
}
