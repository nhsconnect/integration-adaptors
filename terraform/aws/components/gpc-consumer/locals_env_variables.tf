locals {
  environment_variables = concat(var.gpc-consumer_environment_variables,[
    {
      name  = "GPC_CONSUMER_SERVER_PORT"
      value = var.gpc-consumer_service_container_port
    },
    {
      name  = "GPC_CONSUMER_ROOT_LOGGING_LEVEL"
      value = var.gpc-consumer_root_log_level
    },
    {
      name  = "GPC_CONSUMER_ROOT_LOGGING_LEVEL"
      value = var.gpc-consumer_log_level
    },
    {
      name  = "GPC_CONSUMER_LOGGING_FORMAT"
      value = var.gpc-consumer_logging_format
    },
    {
      name  = "GPC_CONSUMER_URL"
      value = "http://${module.gpc-consumer_ecs_service[0].loadbalancer_dns_name}:${var.gpc-consumer_service_container_port}"
    },
    {
      name  = "GPC_CONSUMER_GPC_GET_URL"
      value = var.gpc-consumer_create_wiremock ? "http://${module.gpc-consumer_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gpc-consumer_wiremock_container_port}" : ""
    },
    {
      name  = "GPC_CONSUMER_SDS_URL"
      value = var.gpc-consumer_create_wiremock ? "http://${module.gpc-consumer_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gpc-consumer_wiremock_container_port}" : var.gpc-consumer_sds_url
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
      name = "GPC_CONSUMER_MESH_API_HTTP_PROXY"
      value = var.opentest_connected ? data.aws_instance.opentest_instance.private_ip : ""
    },
    {
      name = "GPC_CONSUMER_AMQP_BROKERS"
      value = replace(data.aws_mq_broker.gpc-consumer_mq_broker.instances[0].endpoints[1],"amqp+ssl","amqps") # https://www.terraform.io/docs/providers/aws/r/mq_broker.html#attributes-reference
    },
    {
      name = "GPC_CONSUMER_MESH_OUTBOUND_QUEUE_NAME"
      value = "${var.environment}_gpc-consumer_mesh_outbound"
    },
    {
      name = "GPC_CONSUMER_MESH_INBOUND_QUEUE_NAME"
      value = "${var.environment}_gpc-consumer_mesh_inbound"
    },
    {
      name = "GPC_CONSUMER_GP_SYSTEM_INBOUND_QUEUE_NAME"
      value = "${var.environment}_gpc-consumer_gp_system_inbound"
    },
    {
      name = "GPC_CONSUMER_AMQP_MAX_RETRIES"
      value = var.gpc-consumer_amqp_max_retries
    },
    {
      name = "GPC_CONSUMER_AMQP_RETRY_DELAY"
      value = var.gpc-consumer_amqp_retry_delay
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
      name = "GPC_CONSUMER_MESH_HOST"
      value = var.gpc-consumer_mesh_host
    },
    {
      name = "GPC_CONSUMER_MESH_CERT_VALIDATION"
      value = var.gpc-consumer_mesh_cert_validation
    },
    {
      name = "GPC_CONSUMER_MESH_POLLING_CYCLE_MINIMUM_INTERVAL_IN_SECONDS"
      value = var.gpc-consumer_mesh_polling_cycle_minimum_interval_in_seconds
    },
    {
      name = "GPC_CONSUMER_MESH_CLIENT_WAKEUP_INTERVAL_IN_MILLISECONDS"
      value = var.gpc-consumer_mesh_client_wakeup_interval_in_milliseconds
    },
    {
      name = "GPC_CONSUMER_MESH_POLLING_CYCLE_DURATION_IN_SECONDS",
      value = var.gpc-consumer_mesh_polling_cycle_duration_in_seconds
    },
    {
      name = "GPC_CONSUMER_SCHEDULER_ENABLED"
      value = var.gpc-consumer_scheduler_enabled
    },
    {
      name = "GPC_CONSUMER_SSL_TRUST_STORE_URL"
      value = var.gpc-consumer_ssl_trust_store_url
    }
  ])
}
