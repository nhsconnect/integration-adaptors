output "nhais_ecr_repo_url" {
  value = aws_ecr_repository.nhais_ecr_repository.repository_url
}

output "nhais_ecr_repo_name" {
  value = aws_ecr_repository.nhais_ecr_repository.name
}