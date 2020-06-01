resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.base_vpc.id
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-igw"
  })
}
