output "vpc_id" {
  value = aws_vpc.mhs_vpc.id
  description = "VPC ID of the MHS component"
}

output "subnet_ids" {
  value = aws_subnet.mhs_subnet.*.id
  description = "IDs of subnets used in MHS Component"
}

output "cluster_id" {
  value = aws_ecs_cluster.mhs_cluster.id
  description = "ID of ECS Cluster created by this component"
}

output "cluster_name" {
  value = aws_ecs_cluster.mhs_cluster.name
  description = "Name of ECS Cluster created by this component"
}

output "cloudwatch_vpce_security_group_id" {
  value = aws_security_group.cloudwatch_security_group.id
  description = "ID of security group for cloudwatch VPC Endpoint"
}

output "ecr_vpce_security_group_id" {
  value =  aws_security_group.ecr_security_group.id
  description = "ID of security group for ECR VPC endpoint"
}

output "s3_endpoint_prefix_list_ids" {
  value = aws_vpc_endpoint.s3_endpoint.prefix_list_id
  description = "IDs of Prefix list provided by S3 endpoint"
}
