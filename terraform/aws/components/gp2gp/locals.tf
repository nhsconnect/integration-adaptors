locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"

  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  # Use below when the ECR repo is created by terraform in account component.
  #image_name = "${data.terraform_remote_state.account.outputs.ecr_repo_url_gp2gp}:${var.gp2gp_build_id}"
  image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/gp2gp:${var.gp2gp_build_id}"
  mhs_mock_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/gp2gp-mock-mhs:${var.gp2gp_mhs_mock_build_id}"
  wiremock_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/gp2gp-wiremock:${var.gp2gp_build_id}"
  
  lb_type = "application"
  protocol = "HTTP"

  subnet_cidrs = [
    cidrsubnet(data.terraform_remote_state.base.outputs.gp2gp_cidr,2,0),
    cidrsubnet(data.terraform_remote_state.base.outputs.gp2gp_cidr,2,1),
    cidrsubnet(data.terraform_remote_state.base.outputs.gp2gp_cidr,2,2)
  ]

}
