module "mhs_route_ecs_service" {
  source = "../../modules/module_ecs_service"

  project         = var.project
  component       = var.component
  environment     = var.environment
  region          = var.region
  module_instance = "mhs_route_ecs"
  default_tags    = local.default_tags
  
  availability_zones = local.availability_zones

  image_name        = local.route_image_name
  cluster_id        = data.terraform_remote_state.base.outputs.base_cluster_id
  minimal_count     = var.mhs_service_minimal_count
  desired_count     = var.mhs_service_desired_count
  maximal_count     = var.mhs_service_maximal_count
  service_target_request_count = var.mhs_service_target_request_count

  container_port    = var.mhs_route_service_container_port
  application_port  = var.mhs_service_application_port
  launch_type       = var.mhs_service_launch_type
  log_stream_prefix = var.mhs_build_id
  healthcheck_path  = var.mhs_healthcheck_path
  enable_load_balancing = true
  use_application_lb = true
  load_balancer_type = "application"
  protocol = "HTTP"
  logs_datetime_format = var.logs_datetime_format

  container_healthcheck_port =  var.mhs_route_service_container_port
  enable_dlt                 = var.enable_dlt
  dlt_vpc_id                 = var.dlt_vpc_id

  environment_variables = local.route_variables
  secret_variables      = local.secret_variables

  task_execution_role_arn = aws_iam_role.ecs_service_task_execution_role.arn
  task_role_arn           = data.aws_iam_role.ecs_service_task_role.arn
  task_scaling_role_arn   = data.aws_iam_role.ecs_autoscale_role.arn
  
  additional_security_groups = [
    data.terraform_remote_state.base.outputs.core_sg_id,
    data.terraform_remote_state.base.outputs.docdb_access_sg_id
  ]

  lb_allowed_security_groups = [
    data.terraform_remote_state.account.outputs.jumpbox_sg_id,
    module.mhs_outbound_ecs_service.service_sg_id
  ]

  additional_container_config =  []

  create_testbox=false //create testbox only along the inbound service
  jumpbox_sg_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
  vpc_id = data.terraform_remote_state.base.outputs.vpc_id
  lb_subnet_ids = data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids : aws_subnet.service_subnet.*.id
  container_subnet_ids= data.terraform_remote_state.base.outputs.ptl_connected ? data.terraform_remote_state.base.outputs.ptl_container_subnet_ids : aws_subnet.service_subnet.*.id
}
