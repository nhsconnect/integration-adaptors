locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"

  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  gp2gp_translator_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/pss_gp2gp-translator:${var.gp2gp_translator_build_id}"
  mhs_mock_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/pss-mock-mhs:${var.pss_mhs_mock_build_id}"
  gpc_api_facade_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/pss_gpc_facade:${var.gpc_api_facade_build_id}"


  subnet_cidrs = [
    cidrsubnet(data.terraform_remote_state.base.outputs.pss_cidr,2,0),
    cidrsubnet(data.terraform_remote_state.base.outputs.pss_cidr,2,1),
    cidrsubnet(data.terraform_remote_state.base.outputs.pss_cidr,2,2)
  ]
}
