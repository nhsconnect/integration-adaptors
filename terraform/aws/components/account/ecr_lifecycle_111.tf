resource "aws_ecr_lifecycle_policy" "ecr_policy_111" {
  repository = aws_ecr_repository.ecr_repository_111.name 
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
        },
        {
          rulePriority = 2
          description = "Keep last 10 master images"
          selection = {
            tagStatus = "tagged"
            tagPrefixList = ["master"]
            countType = "imageCountMoreThan"
            countNumber = 10
          }
          action = {
            type = "expire"
          }
        }

      ]
    }
  )
}
