locals {
  environment_variables = concat(var.lab-results_environment_variables,[
    {
      name = "LAB_RESULTS_MESH_API_HTTP_PROXY"
      value = var.opentest_connected ? data.aws_instance.opentest_instance.private_ip : ""
    },
    {
      name  = "LAB_RESULTS_OUTBOUND_SERVER_PORT"
      value = var.lab-results_service_container_port
    },
    {
      name = "LAB_RESULTS_AMQP_BROKERS"
      value = replace(data.aws_mq_broker.lab-results_mq_broker.instances[0].endpoints[1],"amqp+ssl","amqps") # https://www.terraform.io/docs/providers/aws/r/mq_broker.html#attributes-reference
    },
    {
      name = "LAB_RESULTS_MESH_OUTBOUND_QUEUE_NAME"
      value = "${var.environment}_lab-results_mesh_outbound"
    },
    {
      name = "LAB_RESULTS_MESH_INBOUND_QUEUE_NAME"
      value = "${var.environment}_lab-results_mesh_inbound"
    },
    {
      name = "LAB_RESULTS_GP_OUTBOUND_QUEUE_NAME"
      value = "${var.environment}_lab-results_gp_outbound"
    },
    {
      name = "LAB_RESULTS_AMQP_MAX_REDELIVERIES"
      value = var.lab-results_amqp_max_redeliveries
    },
    {
      name = "LAB_RESULTS_AMQP_RETRY_DELAY"
      value = var.lab-results_amqp_retry_delay
    },
    {
      name = "LAB_RESULTS_MONGO_DATABASE_NAME"
      value = "labresults"
    },
    {
      name  = "LAB_RESULTS_LOGGING_LEVEL"
      value = var.lab-results_log_level
    },
    {
      name = "LAB_RESULTS_MONGO_HOST"
      value = "${data.terraform_remote_state.base.outputs.docdb_cluster_endpoint}"
    },
    {
      name = "LAB_RESULTS_MONGO_PORT"
      value = "${data.terraform_remote_state.base.outputs.docdb_instance_port}"
    },
    {
      name = "LAB_RESULTS_MONGO_OPTIONS"
      value = join("&",[var.lab-results_mongo_options,"ssl=${data.terraform_remote_state.base.outputs.docdb_tls_enabled}"])
    },
    {
      name = "LAB_RESULTS_MONGO_AUTO_INDEX_CREATION"
      value = true
    },    
    {
      name = "LAB_RESULTS_MONGO_TTL"
      value = "P30D"
    },
    {
      name = "LAB_RESULTS_COSMOS_DB_ENABLED"
      value = false
    },
    {
      name = "LAB_RESULTS_MESH_HOST"
      value = var.lab-results_mesh_host
    },
    {
      name = "LAB_RESULTS_MESH_CERT_VALIDATION"
      value = var.lab-results_mesh_cert_validation
    },
    {
      name = "LAB_RESULTS_MESH_POLLING_CYCLE_MINIMUM_INTERVAL_IN_SECONDS"
      value = var.lab-results_mesh_polling_cycle_minimum_interval_in_seconds
    },
    {
      name = "LAB_RESULTS_MESH_CLIENT_WAKEUP_INTERVAL_IN_MILLISECONDS"
      value = var.lab-results_mesh_client_wakeup_interval_in_milliseconds
    },
    {
      name = "LAB_RESULTS_MESH_POLLING_CYCLE_DURATION_IN_SECONDS",
      value = var.lab-results_mesh_polling_cycle_duration_in_seconds
    },
    {
      name = "LAB_RESULTS_SCHEDULER_ENABLED"
      value = var.lab-results_scheduler_enabled
    },
    {
      name = "LAB_RESULTS_SSL_TRUST_STORE_URL"
      value = var.lab-results_ssl_trust_store_url
    },
    {
      name = "LAB_RESULTS_LOGGING_APPENDER"
      value = "TEXT"
    }
  ])
}
