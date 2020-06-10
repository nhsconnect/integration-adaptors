resource "aws_ecr_lifecycle_policy" "ecr_policy" {
  count = length(var.ecr_repositories)
  repository = aws_ecr_repository.ecr_repository[count.index].name
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
            countNumber = var.ecr_repositories[count.index].expire_PR_after
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
            tagPrefixList = [var.ecr_repositories[count.index].prefix_to_keep]
            countType = "imageCountMoreThan"
            countNumber = var.ecr_repositories[count.index].number_to_keep
          }
          action = {
            type = "expire"
          }
        }
      ]
    }
  )
}