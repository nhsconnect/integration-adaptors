locals {
  # variables common for all three adapters
  environment_variables = concat(var.mhs_environment_variables,[
    {
      name = "MHS_LOG_LEVEL"
      value = var.mhs_log_level
    },
    {
      name = "MHS_STATE_TABLE_NAME"
      value = "${var.environment}_mhs_state"
    },
    {
      name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
      value = "${var.environment}_mhs_sync_async"
    },
    {
      name = "MHS_PERSISTENCE_ADAPTOR"
      value = "mongodb"
    },
    {
      name = "MHS_DB_ENDPOINT_URL"
      value = join("&",[data.terraform_remote_state.base.outputs.docdb_cluster_connection_string,"ssl=${data.terraform_remote_state.base.outputs.docdb_tls_enabled}"])
    },
    {
      name  = "MHS_OUTBOUND_ROUTING_LOOKUP_METHOD"
      value = "SDS_API"
    },
    {
      name  = "MHS_SDS_API_URL"
      value = var.gpc-consumer_sds_url
    }
  ])

  outbound_variables = concat(local.environment_variables, [
    {
      name = "MHS_SPINE_ROUTE_LOOKUP_URL"
      value = "http://${aws_route53_record.mhs_route_lb_record.name}"
    },
    {
      name = "MHS_OUTBOUND_VALIDATE_CERTIFICATE"
      value = var.mhs_outbound_validate_certificate
    },
    {
      name = "MHS_OUTBOUND_SPINE_ROUTE_LOOKUP_VALIDATE_CERT"
      value = var.mhs_outbound_spineroutelookup_validate_certificate
    },
    {
      name = "MHS_FORWARD_RELIABLE_ENDPOINT_URL"
      value = var.mhs_outbound_forward_reliable_url
    },
    {
      name = "MHS_OUTBOUND_HTTP_PROXY"
      value = var.opentest_connected ? data.aws_instance.opentest_instance.private_ip : ""
    },
    {
      name = "MHS_RESYNC_INITIAL_DELAY"
      value = "0.15"
    },
    {
      name = "MHS_RESYNC_INTERVAL"
      value = "1"
    },
    {
      name = "MHS_RESYNC_RETRIES"
      value = "20"
    },
    {
      name = "MHS_SPINE_ORG_CODE"
      value = var.mhs_spine_org_code
    },
    {
      name = "MHS_SPINE_REQUEST_MAX_SIZE"
      value = "4999600"
    },
  ])

  inbound_variables = concat(local.environment_variables, [
    {
      name = "MHS_INBOUND_QUEUE_BROKERS"
      value = replace(data.aws_mq_broker.nhais_mq_broker.instances[0].endpoints[1], "amqp+ssl", "amqps")
    },
    {
      name = "MHS_INBOUND_QUEUE_NAME"
      value = var.mhs_inbound_queue_name
    },
    {
      name = "MHS_INBOUND_USE_SSL"
      value = var.mhs_inboud_use_ssl
    }
  ])

  route_variables = concat(local.environment_variables, [
    {
      name = "MHS_SDS_URL"
      value = var.opentest_connected ? "ldap://${data.aws_instance.opentest_instance.private_ip}" : var.mhs_route_sds_url
    },
    {
      name = "MHS_DISABLE_SDS_TLS"
      value = var.mhs_route_disable_sds_tls
    },
    {
      name = "MHS_SDS_SEARCH_BASE"
      value = var.mhs_route_sds_search_base
    },
    {
      name = "MHS_SDS_REDIS_DISABLE_TLS"
      value = var.mhs_route_redis_disable_tls
    },
    {
      name = "MHS_SDS_REDIS_CACHE_HOST"
      value = data.terraform_remote_state.base.outputs.redis_host
    },
    {
      name = "MHS_SDS_REDIS_CACHE_PORT"
      value = data.terraform_remote_state.base.outputs.redis_port
    }
  ])
}
