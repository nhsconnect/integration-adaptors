resource "aws_route53_zone" "base_zone" {
  name = "${var.environment}.${var.root_domain}"
  vpc {
    vpc_id = aws_vpc.base_vpc.id
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-r53_zone"
  })

  # lifecycle {
  #   # Ignore changes to vpc_id as this is managed by aws_route53_zone_association resources.
  #   ignore_changes = [
  #     vpc
  #   ]
  # }
}