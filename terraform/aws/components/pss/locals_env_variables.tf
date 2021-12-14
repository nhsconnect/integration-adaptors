locals {
    pss_gpc_api_facade_environment_variables = [
      {
        name = "GPC_SERVER_PORT"
        value = var.gpc_api_facade_container_port
      },
      {
        name = "PS_DB_URL"
        value = "jdbc:postgresql://${var.postgres_master_user}:${var.postgres_master_password}@${aws_db_instance.base_postgres_db[0].address}:${aws_db_instance.base_postgres_db[0].port}/patient_switching"
      },
      {
        name = "GPC_USER_DB_PASSWORD"
        value = var.postgres_master_password
      },
      {
        name = "PSS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "PSS_QUEUE_NAME"
        value = var.mq_broker_name
      },
      {
        name = "PSS_AMQP_USERNAME"
        value = data.aws_secretsmanager_secret.mq_username
      },
      {
        name = "PSS_AMQP_PASSWORD"
        value = data.aws_secretsmanager_secret.mq_password

        name = "PSS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      }
  ]

    pss_gp2gp_translator_environment_variables = [
      {  
        name = "GP2GP_SERVER_PORT"
        value = var.gp2gp_translator_container_port
      },
      {
        name = "PS_DB_URL"
        value = "jdbc:postgresql://${var.postgres_master_user}:${var.postgres_master_password}@${aws_db_instance.base_postgres_db[0].address}:${aws_db_instance.base_postgres_db[0].port}/patient_switching"
      },
      {
        name = "GP2GP_USER_DB_PASSWORD"
        value = var.postgres_master_password
      },
      {
        name = "PSS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.pss_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "MHS_AMQP_BROKER"
        value = replace(data.aws_mq_broker.mhs_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
      },
      {
        name = "PSS_QUEUE_NAME"
        value = var.mq_broker_name
      },
      {
        name = "MHS_QUEUE_NAME"
        value = var.mq_broker_name
      },
      {
        name = "PSS_AMQP_USERNAME"
        value = data.aws_secretsmanager_secret.mq_username
      },
      {
        name = "PSS_AMQP_PASSWORD"
        value = data.aws_secretsmanager_secret.mq_password
      },
      {
        name = "PSS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      },
      {
        name = "MHS_AMQP_USERNAME"
        value = data.aws_secretsmanager_secret.mq_username
      },
      {
        name = "MHS_AMQP_PASSWORD"
        value = data.aws_secretsmanager_secret.mq_password
      },
      {
        name = "MHS_AMQP_MAX_REDELIVERIES"
        value = var.pss_amqp_max_redeliveries
      } 
  ]
}

 mock_mhs_environment_variables = [
    ]