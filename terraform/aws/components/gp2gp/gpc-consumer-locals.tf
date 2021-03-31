locals {
  gpc-consumer_default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  #resource_prefix = "${var.project}-${var.environment}-${var.component}"

  #availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  
  # Use below when the ECR repo is created by terraform in account component.
  #image_name = "${data.terraform_remote_state.account.outputs.nhais_ecr_repo_url}:${var.nhais_build_id}"
  gpc-consumer_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/gpc-consumer:${var.gpc-consumer_build_id}"
  
  #subnet_cidrs = [
  #  cidrsubnet(data.terraform_remote_state.base.outputs.gpc-consumer_cidr,2,0),
  #  cidrsubnet(data.terraform_remote_state.base.outputs.gpc-consumer_cidr,2,1),
  #  cidrsubnet(data.terraform_remote_state.base.outputs.gpc-consumer_cidr,2,2)
  #]
}