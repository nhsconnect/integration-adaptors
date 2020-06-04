locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"

  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  # Use below when the ECR repo is created by terraform in account component.
  image_name = "${data.terraform_remote_state.account.outputs.ecr_repo_url_111}:${var.build_id}"

  subnet_cidrs = [
    cidrsubnet(data.terraform_remote_state.base.outputs.vpc_cidr,3,4),
    cidrsubnet(data.terraform_remote_state.base.outputs.vpc_cidr,3,5),
    cidrsubnet(data.terraform_remote_state.base.outputs.vpc_cidr,3,6)
  ]
}