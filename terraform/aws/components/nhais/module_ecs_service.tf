module "nhais_ecs_service" {
  source = "../../modules/module_ecs_service"

  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "nhais_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = local.image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = var.nhais_service_minimal_count
  desired_count     = var.nhais_service_desired_count
  maximal_count     = var.nhais_service_maximal_count
  service_target_request_count = var.nhais_service_target_request_count

  container_port    = var.nhais_service_container_port
  application_port  = var.nhais_service_application_port
  launch_type       = var.nhais_service_launch_type
  log_stream_prefix = var.nhais_build_id
  healthcheck_path  = var.nhais_healthcheck_path
  enable_load_balancing = true

  container_healthcheck_port = var.nhais_service_container_port
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = local.environment_variables
  secret_variables      = local.secret_variables

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.docdb_access_sg_id,
    aws_security_group.nhais_to_fakemesh.id
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id
  ]

  create_testbox=var.create_testbox
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}

module "fake_mesh_ecs_service" {
  source = "../../modules/module_ecs_service"

  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "fake_mesh_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = "067756640211.dkr.ecr.eu-west-2.amazonaws.com/nhais-fake-mesh:0.2.0" # TODO should replace with a var
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = 1 # fake-mesh does not support multiple instances
  desired_count     = 1
  maximal_count     = 1
  service_target_request_count = 1

  container_port    = 8829
  application_port  = 8829
  launch_type       = var.nhais_service_launch_type
  log_stream_prefix = var.nhais_build_id
  healthcheck_path  = var.nhais_healthcheck_path
  enable_load_balancing = true
  load_balancer_type = "network"
  protocol = "TCP"

  container_healthcheck_port = 8888 # TODO: fake-mesh does not have a healthcheck
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = local.environment_variables
  secret_variables      = local.secret_variables

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.docdb_access_sg_id,
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
    module.nhais_ecs_service.service_sg_id
  ]

  lb_allowed_cidrs = [
    data.terraform_remote_state.base.outputs.nhais_cidr,
    data.terraform_remote_state.account.outputs.account_vpc_cidr,
  ]

  # container_allowed_security_groups =  [
  #   data.terraform_remote_state.account.outputs.jumpbox_sg_id,
  #   module.nhais_ecs_service.service_sg_id
  # ]

  create_testbox=var.create_testbox
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}