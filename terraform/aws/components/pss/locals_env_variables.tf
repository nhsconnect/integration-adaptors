locals {

    environment_variables = [
      {
        name = "PS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "PS_QUEUE_NAME"
        value = "${var.environment}-pss-queue"
      },
      {
        name  = "LOG_LEVEL"
        value = var.pss_log_level
      },
      {
        name = "PS_DB_URL"
        value = "jdbc:postgresql://${data.terraform_remote_state.base.outputs.postgres_instance_endpoint}"
      },
      {
        name = "PS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      }
    ]

    pss_gpc_api_facade_environment_variables = [
      {
        name = "GPC_FACADE_SERVER_PORT"
        value = var.pss_gpc_api_facade_container_port
      }
    ]

    pss_gp2gp_translator_environment_variables = [
      {  
        name = "GP2GP_TRANSLATOR_SERVER_PORT"
        value = var.pss_gp2gp_translator_container_port
      },
      {
        name = "MHS_QUEUE_NAME"
        value = "${var.environment}-pss-mhs-queue"
      },
      {
        name = "MHS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "MHS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      } 
  ]


    mock_mhs_environment_variables = [
    ]
}