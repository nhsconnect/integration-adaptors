output "ecr_repos" {
  value = zipmap(aws_ecr_repository.ecr_repository.*.name, aws_ecr_repository.ecr_repository.*.repository_url)
}

output "account_vpc_id" {
  value = aws_vpc.account_vpc.id
}

output "account_vpc_route_table_id" {
  value = aws_vpc.account_vpc.main_route_table_id
}

output "account_public_route_table_id" {
  value = aws_route_table.public.id
}

output "account_private_route_table_id" {
  value = aws_route_table.private.id
}

output "account_vpc_cidr" {
   value = aws_vpc.account_vpc.cidr_block
}

output "jumpbox_sg_id" {
  description = "ID of jumpbox SG, to be referenced in components that allow access to it"
  value = aws_security_group.jumpbox_sg.id
}

output "jumpbox_hostname" {
  description = "Hostname of jumpbox instance"
  value = aws_instance.jumpbox.public_dns
}

output "rds_iam_role" {
  description = "Iam role arn use to start and stop rds instance"
  value = aws_iam_role.rds_stop_start_role.arn
}
