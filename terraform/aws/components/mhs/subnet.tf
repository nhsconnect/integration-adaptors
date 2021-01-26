resource "aws_subnet" "service_subnet" {
  count = length(local.availability_zones)
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  cidr_block = local.subnet_cidrs[count.index]
  availability_zone = local.availability_zones[count.index]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-subnet-${count.index}"
  })
}
