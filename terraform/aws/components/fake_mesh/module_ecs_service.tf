module "fake_mesh_ecs_service" {
  source = "../../modules/module_ecs_service"

  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "fake_mesh_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = local.image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = 1 # fake-mesh does not support multiple instances
  desired_count     = 1
  maximal_count     = 1
  service_target_request_count = 1200

  container_port    = 8829
  application_port  = 8829
  launch_type       = var.fake_mesh_service_launch_type
  log_stream_prefix = var.fake_mesh_version
  healthcheck_path  = var.fake_mesh_healthcheck_path
  enable_load_balancing = true
  use_application_lb = false
  load_balancer_type = "network"
  protocol = "TCP"

  container_healthcheck_port = 8888
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = []
  secret_variables      = []

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.docdb_access_sg_id,
  ]

  lb_allowed_security_groups = [
      data.terraform_remote_state.lab-results.outputs.lab-results_external_access_sg_id
//    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
//    module.nhais_ecs_service.service_sg_id // TODO
  ]

  lb_allowed_cidrs = [
    data.terraform_remote_state.base.outputs.nhais_cidr,
    data.terraform_remote_state.account.outputs.account_vpc_cidr,
  ]

  container_allowed_security_groups =  [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
//    module.nhais_ecs_service.service_sg_id, // TODO
  ]

  container_allowed_cidrs = [
    data.terraform_remote_state.base.outputs.nhais_cidr,
  ]

  create_testbox=var.create_testbox
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.nhais.outputs.nhais_service_subnets
  container_subnet_ids= data.terraform_remote_state.nhais.outputs.nhais_service_subnets
}
