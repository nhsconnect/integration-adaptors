output "vpc_id" {
  value = aws_vpc.base_vpc.id
}

output "base_cluster_id" {
  value = module.base_ecs_cluster.cluster_id
}

output "base_cluster_name" {
  value = module.base_ecs_cluster.cluster_name
}

output "vpc_cidr" {
  value = aws_vpc.base_vpc.cidr_block
}

output "core_sg_id" {
  value = aws_security_group.core_sg.id
}

output "cloudwatch_vpce_id" {
  value = aws_vpc_endpoint.cloudwatch_endpoint.id
}

output "ecr_vpce_id" {
  value = aws_vpc_endpoint.ecr_endpoint.id
}

output "private_nat_gw_route_table" {
  value = aws_route_table.private.id
}

output "r53_zone_id" {
  value = aws_route53_zone.base_zone.zone_id
}

output "r53_zone_name" {
  value = aws_route53_zone.base_zone.name
}

output "docdb_cluster_endpoint" {
  value = aws_docdb_cluster.base_db_cluster.endpoint
}

output "docdb_instance_port" {
  value = aws_docdb_cluster_instance.base_db_instance[0].port
}

output "docdb_access_sg_id" {
  value = aws_security_group.docdb_access_sg.id
}

output "nhais_cidr" {
  value = local.nhais_cidr
  description = "CIDR block for NHAIS component"
}

output "OneOneOne_cidr" {
  value = local.OneOneOne_cidr
  description = "CIDR block for OneOneOne component"
}

output "scr_cidr" {
  value = local.scr_cidr
  description = "CIDR block for SCR component"
}

output "mhs_cidr" {
  value = local.mhs_cidr
  description = "CIDR block for MHS component"
}

# PTL section

output "ptl_connected" {
  value = var.ptl_connected
}

output "ptl_assigned_cidr" {
  value = var.ptl_connected ? var.ptl_assigned_cidr : null
}

# output "ptl_container_subnet_ids" {
#   value = var.ptl_connected ? aws_subnet.service_containers_subnet.*.id : null
# }

# output "ptl_lb_subnet_ids" {
#   value = var.ptl_connected ? aws_subnet.service_lb_subnet.*.id : null
# }


output "ptl_container_subnet_ids" {
  value = aws_subnet.service_containers_subnet.*.id
}

output "ptl_lb_subnet_ids" {
  value = aws_subnet.service_lb_subnet.*.id
}
