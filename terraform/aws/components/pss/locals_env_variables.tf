locals {

    environment_variables = [
      {
        name = "PS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "PS_QUEUE_NAME"
        value = var.pss_queue_name
      },
      {
        name = "PS_DB_URL"
        value = "jdbc:${data.terraform_remote_state.base.outputs.postgres_instance_connection_string}/patient_switching"
      },
      {
        name = "PS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      }
    ]

    pss_gpc_api_facade_environment_variables = [
      {
        name = "GPC_SERVER_PORT"
        value = var.pss_service_application_port
      }
    ]

    pss_gp2gp_translator_environment_variables = [
      {  
        name = "GP2GP_SERVER_PORT"
        value = var.pss_service_application_port
      },
      {
        name = "MHS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "MHS_QUEUE_NAME"
        value = var.mhs_queue_name
      },
      {
        name = "MHS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      } 
  ]


    mock_mhs_environment_variables = [
    ]
}