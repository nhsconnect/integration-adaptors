output "vpc_id" {
  value = aws_vpc.mhs_vpc.id
  description = "VPC ID of the MHS component"
}

output "subnet_ids" {
  value = aws_subnet.mhs_subnets.*.id
  description = "IDs of subnets used in MHS Component"
}