locals {
  environment_variables = concat(var.gp2gp_environment_variables, [
    {
      name  = "GP2GP_LOGGING_LEVEL"
      value = var.gp2gp_log_level
    },
    {
      name  = "GP2GP_MONGO_HOST"
      value = data.terraform_remote_state.base.outputs.docdb_cluster_endpoint
    },
    {
      name  = "GP2GP_MONGO_PORT"
      value = data.terraform_remote_state.base.outputs.docdb_instance_port
    },
    {
      name  = "GP2GP_MONGO_DATABASE_NAME"
      value = "gp2gp"
    },
    {
      name  = "GP2GP_MONGO_TTL"
      value = "P30D"
    },
    {
      name  = "GP2GP_AMQP_BROKERS"
      value = replace(data.aws_mq_broker.nhais_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps") # https://www.terraform.io/docs/providers/aws/r/mq_broker.html#attributes-reference
    },
    {
      name  = "GP2GP_MHS_INBOUND_QUEUE"
      value = var.mhs_inbound_queue_name
    },
    {
      name  = "GP2GP_TASK_QUEUE"
      value = join("-", list(var.environment, "gp2gp", "tasks"))
    },
    {
      name = "GP2GP_GPC_GET_STRUCTURED_ENDPOINT"
      value = var.gp2gp_gpc_get_structured_endpoint
    },
    {
      name = "GP2GP_GPC_GET_DOCUMENT_ENDPOINT"
      value = var.gp2gp_gpc_get_document_endpoint
    },
    {
      name = "GP2GP_STORAGE_TYPE"
      value = "S3"
    },
   {
      name = "GP2GP_STORAGE_CONTAINER_NAME"
      value = aws_s3_bucket.gp2gp_extract_cache_bucket.id
    },
    {
      name = "GP2GP_GPC_HOST"
      value = var.gp2gp_gpc_host
    },
    {
      name = "GP2GP_GPC_GET_URL"
      value = var.gp2gp_create_wiremock ? "${module.gp2gp_wiremock_ecs_service[0].loadbalancer_dns_name}:${var.gp2gp_wiremock_container_port}/GP0001/STU3/1/gpconnect" : var.gp2gp_gpc_get_url
    }
  ])
}
