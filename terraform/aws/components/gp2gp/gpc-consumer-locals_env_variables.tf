locals {
  gpcc_environment_variables = concat(var.gpc-consumer_environment_variables,[
    {
      name  = "GPC_CONSUMER_SERVER_PORT"
      value = var.gpc-consumer_service_container_port
    },
    {
      name  = "GPC_CONSUMER_ROOT_LOGGING_LEVEL"
      value = var.gpc-consumer_root_log_level
    },
    {
      name  = "GPC_CONSUMER_LOGGING_LEVEL"
      value = var.gpc-consumer_log_level
    },
    {
      name  = "GPC_CONSUMER_LOGGING_FORMAT"
      value = var.gpc-consumer_logging_format
    },
    {
      name  = "GPC_CONSUMER_URL"
      value = "http://${module.gpc-consumer_ecs_service.loadbalancer_dns_name}:${var.gpc-consumer_service_container_port}"
    },
    {
      name  = "GPC_CONSUMER_GPC_GET_URL"
      value = var.gp2gp_create_wiremock ? "http://${module.gp2gp_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gp2gp_wiremock_container_port}" : "https://orange.testlab.nhs.uk"
    },
    {
      name  = "GPC_CONSUMER_SDS_URL"
      value = var.gp2gp_create_wiremock ? "http://${module.gp2gp_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gp2gp_wiremock_container_port}" : var.gpc-consumer_sds_url
    },
    {
      name  = "GPC_CONSUMER_SSP_FQDN"
      value = var.gpc-consumer_ssp_fqdn
    }
  ])
}