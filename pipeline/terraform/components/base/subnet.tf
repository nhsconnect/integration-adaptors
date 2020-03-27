# Create a private subnet in each availability zone in the region.
resource "aws_subnet" "mhs_subnet" {
  count = length(data.aws_availability_zones.all.names)

  vpc_id = aws_vpc.base_vpc.id
  availability_zone = data.aws_availability_zones.all.names[count.index]

  # Generates a CIDR block with a different prefix within the VPC's CIDR block for each subnet being created.
  # E.g if the VPC's CIDR block is 10.0.0.0/16, this generates subnets that have CIDR blocks 10.0.0.0/24, 10.0.1.0/24,
  # etc.
  cidr_block = cidrsubnet(var.mhs_vpc_cidr_block, 8, count.index)

  map_public_ip_on_launch = false

  tags = {
    Name = "${var.environment_id}-base-subnet-${data.aws_availability_zones.all.names[count.index]}"
    EnvironmentId = var.environment_id
  }
}