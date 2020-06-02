locals {
  environment_variables = concat(var.environment_variables,[
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
      name = "NHAIS_MONGO_URI"
      value = "mongodb://${var.docdb_master_user}:${var.docdb_master_password}@${aws_docdb_cluster.nhais_db_cluster.endpoint}:${aws_docdb_cluster_instance.nhais_db_instance[0].port}"
    },
    {
      name  = "NHAIS_LOG_LEVEL"
      value = var.nhais_log_level
    },
    {
      name = "NHAIS_MONGO_USERNAME"
      value = var.docdb_master_user
    },
    {
      name = "NHAIS_MONGO_PASSWORD"
      value = var.docdb_master_password
    }
  ])
}
