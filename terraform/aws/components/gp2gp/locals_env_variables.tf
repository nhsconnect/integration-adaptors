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
    }
  ])
}
