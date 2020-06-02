resource "aws_ecr_repository" "nhais_ecr_repository" {
  name = var.nhais_ecr_repository_name
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-nhais_ecr"
  })
}