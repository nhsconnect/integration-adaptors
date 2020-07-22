resource "aws_security_group" "r53_resolver_sg" {
  count = var.ptl_connected ? 1 : 0
  name = "${local.resource_prefix}-r53_resolver_sg"
  description = "Security group route53 resolver in env: ${var.environment}"
  vpc_id = aws_vpc.base_vpc.id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-r53_resolver_sg"
  })
}
