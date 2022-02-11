module "ecs_service_mock_mhs" {
  source = "../../modules/module_ecs_service"

  count           = var.pss_create_mhs_mock ? 1 : 0
  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "ps_mhs_mock_ecs"
  default_tags    = local.default_tags

  availability_zones = local.availability_zones

  image_name        = local.pss_mhs_mock_image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = var.pss_service_minimal_count
  desired_count     = var.pss_service_desired_count
  maximal_count     = var.pss_service_maximal_count
  service_target_request_count = var.pss_service_target_request_count
  ecs_scheduler_stop_time = var.ecs_scheduler_stop_pattern
  ecs_scheduler_start_time = var.ecs_scheduler_start_pattern
  enable_ecs_schedule = var.enable_ecs_scheduler
  ecs_schedule_stop_capacity = var.ecs_scheduler_stop_capacity
  ecs_schedule_start_capacity = var.pss_service_maximal_count

  container_port    = var.pss_mock_mhs_port
  application_port  = var.pss_mock_mhs_port
  launch_type       = var.pss_service_launch_type
  log_stream_prefix = var.pss_build_id
  healthcheck_path  = var.pss_healthcheck_path
  enable_load_balancing = true
  use_application_lb = true
  load_balancer_type = "application"
  protocol = "HTTP"

  container_healthcheck_port = var.pss_mock_mhs_port
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = local.mock_mhs_environment_variables
  secret_variables      = local.secret_variables

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn

  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.postgres_access_sg_id
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
    aws_security_group.pss_testbox_sg.id,
    module.ecs_service_gp2gp_translator.service_sg_id,
    module.ecs_service_gpc_api_facade.service_sg_id
  ]

  container_allowed_security_groups =  [
    aws_security_group.pss_container_access_sg.id
  ]

  additional_container_config = []

  logs_datetime_format = var.pss_logs_datetime_format

  create_testbox = false
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}