resource "aws_ecr_lifecycle_policy" "nhais_policy" {
  repository = aws_ecr_repository.nhais_ecr_repository.name 
  policy = jsonencode(
    {
      rules = [
        {
          rulePriority = 1
          description = "Expire images from PRs older than 14 days"
          selection = {
            tagStatus = "tagged"
            tagPrefixList = ["PR"]
            countType = "sinceImagePushed"
            countUnit = "days"
            countNumber = 14
          }
          action = {
            type = "expire"
          }
        }
      ]
    }
  )
}