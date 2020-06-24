# output "nhais_ecr_repo_url" {
#   value = aws_ecr_repository.nhais_ecr_repository.repository_url
# }

# output "nhais_ecr_repo_name" {
#   value = aws_ecr_repository.nhais_ecr_repository.name
# }

# output "ecr_repo_url_111" {
#   value = aws_ecr_repository.ecr_repository_111.repository_url
# }

# output "ecr_repo_name_111" {
#   value = aws_ecr_repository.ecr_repository_111.name
# }

output "ecr_repo_urls" {
  value = aws_ecr_repository.*.repository_url
}

output "ecr_repo_names" {
  value = aws_ecr_repository.*.name
}

output "jumpbox_sg_id" {
  description = "ID of jumpbox SG, to be referenced in components that allow access to it"
  value = aws_security_group.jumpbox_sg.id
}
