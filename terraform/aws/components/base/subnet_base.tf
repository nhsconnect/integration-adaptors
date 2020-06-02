resource "aws_subnet" "base_subnet" {
  //count = length(var.subnet_cidrs)
  vpc_id = aws_vpc.base_vpc.id
  cidr_block = cidrsubnet(aws_vpc.base_vpc.cidr_block,3,0)

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-subnet"
  })
}
