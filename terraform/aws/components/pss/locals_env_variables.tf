locals {
    mock_mhs_environment_variables = [
        {
        name = "MOCK_MHS_SERVER_PORT"
        value = var.pss_mock_mhs_port
        },
        {
        name = "MOCK_MHS_LOGGING_LEVEL"
        value = var.pss_log_level
        },
        {
        name = "pss_MHS_INBOUND_QUEUE"
        value = var.mhs_inbound_queue_name
        },
        {
        name  = "pss_AMQP_BROKERS"
        value = replace(data.aws_mq_broker.nhais_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
        },
        {
        name = "GP2GP_AMQP_MAX_REDELIVERIES"
        value = var.pss_mock_mhs_amqp_max_redeliveries
        },
        {
        name = "MHS_MOCK_REQUEST_JOURNAL_ENABLED"
        value = false
        },
        {
        name = "MHS_MOCK_ROOT_LOGGING_LEVEL"
        value = "WARN"
        },
    ]

    gpc_api_facade_environment_variables = [
  ]

    gp2gp_translator_environment_variables = [
  ]
}