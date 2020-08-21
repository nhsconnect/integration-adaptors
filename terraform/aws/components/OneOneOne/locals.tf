locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"

  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  # Use below when the ECR repo is created by terraform in account component.
  #image_name = "${data.terraform_remote_state.account.outputs.ecr_repo_url_111}:${var.OneOneOne_build_id}"
  image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/111:${var.OneOneOne_build_id}"

  lb_type = var.OneOneOne_use_nginx_proxy ? "network" : "application"
  protocol = var.OneOneOne_use_nginx_proxy ? "TCP" : "HTTP"

  subnet_cidrs = [
    cidrsubnet(data.terraform_remote_state.base.outputs.OneOneOne_cidr,2,0),
    cidrsubnet(data.terraform_remote_state.base.outputs.OneOneOne_cidr,2,1),
    cidrsubnet(data.terraform_remote_state.base.outputs.OneOneOne_cidr,2,2)
  ]

}