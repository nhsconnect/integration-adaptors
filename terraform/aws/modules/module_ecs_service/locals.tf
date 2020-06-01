locals {
  resource_prefix = "${var.project}-${var.environment}-${var.module_instance}"
  
  default_tags = merge(var.default_tags,{
    Module          = var.module_name,
    Module_Instance = var.module_instance,
  })

  container_name = "${local.resource_prefix}-container"

  load_balancer_default_settings = [
    {
      target_group_arn = aws_lb_target_group.service_target_group[0].arn
      container_name = local.container_name
      container_port = var.container_port
    }
  ]

  load_balancer_settings = var.enable_load_balancing ? local.load_balancer_default_settings : []

  healthcheck_port = var.container_healthcheck_port == 0 ? var.container_port : var.container_healthcheck_port

  application_mapping = [
    {
      containerPort = var.container_port
      hostPort = var.container_port
      protocol = var.container_protocol
    }
  ]

  healthcheck_mapping = local.healthcheck_port == var.container_healthcheck_port ? [] : [
    {
      containerPort = var.container_healthcheck_port
      hostPort = var.container_healthcheck_port
      protocol = var.container_protocol
    }
  ]

  port_mappings = concat(local.application_mapping,local.healthcheck_mapping)
}


