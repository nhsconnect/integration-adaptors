resource "aws_ecr_repository" "ecr_repository" {
  count = length(var.ecr_repositories)
  name = var.ecr_repositories[count.index].name
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = var.ecr_repositories[count.index].scan
  }

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-${var.ecr_repositories[count.index].name}_ecr"
  })
}