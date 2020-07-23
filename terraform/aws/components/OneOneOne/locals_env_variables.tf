locals {
  environment_variables = concat(var.OneOneOne_environment_variables,[
    {
      name = "PEM111_AMQP_BROKER"
      value = replace(data.aws_mq_broker.OneOneOne_mq_broker.instances[0].endpoints[1],"amqp+ssl","amqps") # https://www.terraform.io/docs/providers/aws/r/mq_broker.html#attributes-reference
    },
    {
      name = "PEM111_AMQP_QUEUE_NAME"
      value = "pem111_queue"
    },
    {
      name = "LOG_LEVEL"
      value = var.OneOneOne_log_level
    }
  ])
}
