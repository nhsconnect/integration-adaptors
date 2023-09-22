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
        name  = "PS_LOGGING_LEVEL"
        value = var.pss_log_level
      },
      {
        name = "PS_DB_URL"
        value = "jdbc:postgresql://${data.terraform_remote_state.base.outputs.postgres_instance_endpoint}/patient_switching"
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
        value = "${var.environment}_mhs_inbound"
      },
      {
        name = "MHS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "MHS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      },
      {
        name = "GP2GP_MHS_INBOUND_QUEUE",
        value = "${var.environment}_gp2gp_queue"
      },
      {
        name = "GP2GP_AMQP_BROKERS",
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "PS_DAISY_CHAINING_ACTIVE",
        value = var.daisy_chaining_active
      },

      {
        name = "MHS_BASE_URL"
        value = "http://${module.ecs_service_mock_mhs[0].loadbalancer_dns_name}:${var.pss_service_application_port}/"
      },
      {
        name = "SUPPORTED_FILE_TYPES"
        value = var.supported_file_types
      }
  ]


    mock_mhs_environment_variables = [
    ]
}