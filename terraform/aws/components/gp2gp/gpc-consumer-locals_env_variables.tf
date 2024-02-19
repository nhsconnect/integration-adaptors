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
      name  = "GPC_CONSUMER_SDS_URL"
      value = var.gp2gp_create_wiremock ? "http://${module.gp2gp_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gp2gp_wiremock_container_port}/spine-directory/" : var.gpc-consumer_sds_url
    },
    {
      name  = "GPC_SUPPLIER_ODS_CODE"
      value = var.gpc-consumer_supplier_ods_code
    },
    {
      name  = "GPC_CONSUMER_SSP_URL"
      value = var.gpc-consumer_ssp_url
    },
  ])
}
