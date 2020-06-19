locals {
  environment_variables = concat(var.nhais_environment_variables,[
    {
      name  = "NHAIS_OUTBOUND_SERVER_PORT"
      value = var.nhais_service_container_port
    },
    {
      name = "NHAIS_AMQP_BROKERS"
      value = replace(data.aws_mq_broker.nhais_mq_broker.instances[0].endpoints[1],"amqp+ssl","amqps") # https://www.terraform.io/docs/providers/aws/r/mq_broker.html#attributes-reference
    },
    {
      name = "NHAIS_MESH_OUTBOUND_QUEUE_NAME"
      value = "nhais_mesh_outbound"
    },
    {
      name = "NHAIS_MESH_INBOUND_QUEUE_NAME"
      value = "nhais_mesh_inbound"
    },
    {
      name = "NHAIS_AMQP_MAX_RETRIES"
      value = var.nhais_amqp_max_retries
    },
    {
      name = "NHAIS_AMQP_RETRY_DELAY"
      value = var.nhais_amqp_retry_delay
    },
    {
      name = "NHAIS_MONGO_DATABASE_NAME"
      value = "nhais"
    },
    {
      name  = "NHAIS_LOG_LEVEL"
      value = var.nhais_log_level
    },
    {
      name = "NHAIS_MONGO_HOST"
      value = "${data.terraform_remote_state.base.outputs.docdb_cluster_endpoint}"
    },
    {
      name = "NHAIS_MONGO_PORT"
      value = "${data.terraform_remote_state.base.outputs.docdb_instance_port}"
    },
    {
      name = "NHAIS_MONGO_OPTIONS"
      value = var.nhais_mongo_options
    }
  ])
}
