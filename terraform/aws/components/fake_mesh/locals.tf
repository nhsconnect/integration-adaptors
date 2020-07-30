locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"

  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]

  image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/nhais-fake-mesh:${var.fake_mesh_version}"
  // 067756640211.dkr.ecr.eu-west-2.amazonaws.com/nhais-fake-mesh:0.2.0"
  # Use below when the ECR repo is created by terraform in account component.

  subnet_cidrs = [
    cidrsubnet(data.terraform_remote_state.base.outputs.nhais_cidr,2,0),
    cidrsubnet(data.terraform_remote_state.base.outputs.nhais_cidr,2,1),
    cidrsubnet(data.terraform_remote_state.base.outputs.nhais_cidr,2,2)
  ]
}
