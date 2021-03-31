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
      name  = "GPC_CONSUMER_SDS_URL"
      value = var.gp2gp_create_wiremock ? "http://${module.gp2gp_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gp2gp_wiremock_container_port}" : var.gpc-consumer_sds_url
    },
    {
      name  = "GPC_CONSUMER_GPC_STRUCTURED_PATH"
      value = "/GP0001/STU3/1/gpconnect/fhir/Patient/$gpc.getstructuredrecord"
    },
    {
      name  = "GPC_CONSUMER_GPC_GET_DOCUMENT_PATH"
      value = "/GP0001/STU3/1/gpconnect/fhir/Binary/{documentId}"
    },
    {
      name  = "GPC_CONSUMER_GPC_GET_PATIENT_PATH"
      value = "/GP0001/STU3/1/gpconnect/fhir/Patient"
    },
    {
      name  = "GPC_CONSUMER_SEARCH_DOCUMENTS_PATH"
      value = "/GP0001/STU3/1/gpconnect/fhir/Patient/**"
    },
    {
      name  = "GPC_CONSUMER_SDS_URL"
      value = var.gpc-consumer_sds_url
    },
    {
      name = "GPC_CONSUMER_MONGO_DATABASE_NAME"
      value = "gpc-consumer"
    },
    {
      name = "GPC_CONSUMER_MONGO_HOST"
      value = "${data.terraform_remote_state.base.outputs.docdb_cluster_endpoint}"
    },
    {
      name = "GPC_CONSUMER_MONGO_PORT"
      value = "${data.terraform_remote_state.base.outputs.docdb_instance_port}"
    },
    {
      name = "GPC_CONSUMER_MONGO_OPTIONS"
      value = join("&",[var.gpc-consumer_mongo_options,"ssl=${data.terraform_remote_state.base.outputs.docdb_tls_enabled}"])
    },
    {
      name = "GPC_CONSUMER_SSL_TRUST_STORE_URL"
      value = var.gpc-consumer_ssl_trust_store_url
    }
  ])
}