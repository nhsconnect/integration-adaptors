resource "aws_route53_zone" "mhs_hosted_zone" {
  name = "${var.environment_id}.${var.internal_root_domain}"

  vpc {
    vpc_id = aws_vpc.mhs_vpc.id
  }

  tags = {
    Name = "${var.environment_id}-mhs-hosted-zone"
    EnvironmentId = var.environment_id
  }
}

resource "aws_route53_record" "mhs_outbound_load_balancer_record" {
  zone_id = aws_route53_zone.mhs_hosted_zone.zone_id
  name = "mhs-outbound.${aws_route53_zone.mhs_hosted_zone.name}"
  type = "A"

  alias {
    name = aws_lb.outbound_alb.dns_name
    zone_id = aws_lb.outbound_alb.zone_id
    evaluate_target_health = false
  }
}

output "outbound_lb_domain_name" {
  value = aws_route53_record.mhs_outbound_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS outbound service's load balancer."
}

resource "aws_route53_record" "mhs_route_load_balancer_record" {
  zone_id = aws_route53_zone.mhs_hosted_zone.zone_id
  name = "mhs-route.${aws_route53_zone.mhs_hosted_zone.name}"
  type = "A"

  alias {
    name = aws_lb.route_alb.dns_name
    zone_id = aws_lb.route_alb.zone_id
    evaluate_target_health = false
  }
}

output "route_lb_domain_name" {
  value = aws_route53_record.mhs_route_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS Spine route lookup service's load balancer."
}

resource "aws_route53_record" "mhs_inbound_load_balancer_record" {
  zone_id = aws_route53_zone.mhs_hosted_zone.zone_id
  name = "mhs-inbound.${aws_route53_zone.mhs_hosted_zone.name}"
  type = "A"

  alias {
    name = aws_lb.inbound_nlb.dns_name
    evaluate_target_health = false
    zone_id = aws_lb.inbound_nlb.zone_id
  }
}

output "inbound_lb_domain_name" {
  value = aws_route53_record.mhs_inbound_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS inbound service's load balancer."
}
