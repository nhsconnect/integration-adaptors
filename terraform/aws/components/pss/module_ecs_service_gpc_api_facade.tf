module "ecs_service_gpc_api_facade" {
  source = "../../modules/module_ecs_service"

  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "gpc_facade_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = local.pss_gpc_api_facade_image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = var.pss_service_minimal_count
  desired_count     = var.pss_service_desired_count
  maximal_count     = var.pss_service_maximal_count
  service_target_request_count = var.pss_service_target_request_count

  container_port    = var.pss_gpc_api_facade_container_port
  application_port  = var.pss_service_application_port
  launch_type       = var.pss_service_launch_type
  log_stream_prefix = var.pss_build_id
  healthcheck_path  = var.pss_healthcheck_path
  enable_load_balancing = true
  load_balancer_type = "application"
  
  container_healthcheck_port = var.pss_gpc_api_facade_container_port
  enable_dlt                 = var.enable_dlt
  

  environment_variables = concat(local.pss_gpc_api_facade_environment_variables,local.environment_variables)
  secret_variables      = concat(local.secret_variables,local.pss_gpc_api_facade_secret_variables)

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.postgres_access_sg_id,
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id
  ]

  logs_datetime_format = var.pss_logs_datetime_format

  create_testbox = var.pss_gpc_facade_testbox
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}
