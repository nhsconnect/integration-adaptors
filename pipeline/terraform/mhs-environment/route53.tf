########################################################
# Fixed domain names for MHS load balancers
#
# In lbs.tf, load balancers are defined for the MHS.
# These load balancers are given domain names, but these
# are auto-generated. This file defines Route53 domain
# names that are fixed and are used to make requests to
# MHS load balancers.
########################################################

# The Route53 hosted zone under which we have subdomains pointing to different
# bits of the MHS
resource "aws_route53_zone" "mhs_hosted_zone" {
  name = "${var.environment_id}.${var.internal_root_domain}"
  vpc {
    # Note that if a change is made to vpc_id here, then the lifecycle block below
    # may need to be deleted in order for this to be picked up. But care must be
    # taken when doing this, as this can conflict with other
    # aws_route53_zone_association blocks
    vpc_id = aws_vpc.mhs_vpc.id
  }

  tags = {
    Name = "${var.environment_id}-mhs-hosted-zone"
    EnvironmentId = var.environment_id
  }

  lifecycle {
    # Ignore changes to vpc_id as this is managed by aws_route53_zone_association resources.
    ignore_changes = [
      vpc
    ]
  }
}

# Route53 DNS record that is a domain name pointing to the MHS outbound load balancer
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

# Terraform output variable of the MHS outbound load balancer Route53 domain name
output "outbound_lb_domain_name" {
  value = aws_route53_record.mhs_outbound_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS outbound service's load balancer."
}

# Route53 DNS record that is a domain name pointing to the MHS route service load balancer
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

# Terraform output variable of the MHS route service load balancer Route53 domain name
output "route_lb_domain_name" {
  value = aws_route53_record.mhs_route_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS Spine route lookup service's load balancer."
}

# Route53 DNS record that is a domain name pointing to the MHS inbound load balancer
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

# Terraform output variable of the MHS inbound load balancer Route53 domain name
output "inbound_lb_domain_name" {
  value = aws_route53_record.mhs_inbound_load_balancer_record.name
  description = "The DNS name of the Route53 record pointing to the MHS inbound service's load balancer."
}
