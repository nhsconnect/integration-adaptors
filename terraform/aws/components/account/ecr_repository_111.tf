resource "aws_ecr_repository" "ecr_repository_111" {
  name = var.ecr_repository_name_111
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = false
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-111_ecr"
  })
}