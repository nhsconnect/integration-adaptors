module "gpcapi_mock_ecs_service" {
  source = "../../modules/module_ecs_service"
  count           = var.gp2gp_create_gpcapi_mock ? 1 : 0
  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "gp2gp_gpcapi_mk_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = local.gpcapi_mock_image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = var.gp2gp_service_minimal_count
  desired_count     = var.gp2gp_service_desired_count
  maximal_count     = var.gp2gp_service_maximal_count
  service_target_request_count = var.gp2gp_service_target_request_count

  container_port    = var.gp2gp_mock_port
  application_port  = var.gp2gp_mock_port
  launch_type       = var.gp2gp_service_launch_type
  log_stream_prefix = var.gp2gp_gpcapi_mock_build_id
  healthcheck_path  = var.gp2gp_healthcheck_path
  enable_load_balancing = true

  container_healthcheck_port = var.gp2gp_mock_port
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = local.gpcapi_mock_environment_variables
  secret_variables      = local.gpcc_secret_variables
  command_variables     = local.gpcapi_mock_command_variables


  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.docdb_access_sg_id,
    aws_security_group.gpc-consumer_external_access.id
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
    module.gpc-consumer_ecs_service.service_sg_id
  ]

  additional_container_config = []
  
  logs_datetime_format = var.gpc-consumer_logs_datetime_format


  #create_testbox=var.create_testbox
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}
