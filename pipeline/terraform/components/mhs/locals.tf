# This locals block is used in mhs_outbound_task below to define the
# environment variables
locals {
  mhs_outbound_base_environment_vars = [
    {
      name = "MHS_LOG_LEVEL"
      value = var.mhs_log_level
    },
    {
      name = "MHS_STATE_TABLE_NAME"
      value = aws_dynamodb_table.mhs_state_table.name
    },
    {
      name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
      value = aws_dynamodb_table.mhs_sync_async_table.name
    },
    {
      name = "MHS_RESYNC_RETRIES"
      value = var.mhs_resynchroniser_max_retries
    },
    {
      name = "MHS_RESYNC_INTERVAL"
      value = var.mhs_resynchroniser_interval
    },
    {
      name = "MHS_SPINE_ROUTE_LOOKUP_URL"
      value = "https://${aws_route53_record.mhs_route_load_balancer_record.name}"
    },
    {
      name = "MHS_SPINE_ORG_CODE"
      value = var.mhs_spine_org_code
    },
    {
      name = "MHS_SPINE_REQUEST_MAX_SIZE"
      value = var.mhs_spine_request_max_size
    },
    {
      name = "MHS_FORWARD_RELIABLE_ENDPOINT_URL"
      value = var.mhs_forward_reliable_endpoint_url
    }
  ]
  mhs_outbound_base_secrets = [
    {
      name = "MHS_SECRET_PARTY_KEY"
      valueFrom = var.party_key_arn
    },
    {
      name = "MHS_SECRET_CLIENT_CERT"
      valueFrom = var.client_cert_arn
    },
    {
      name = "MHS_SECRET_CLIENT_KEY"
      valueFrom = var.client_key_arn
    },
    {
      name = "MHS_SECRET_CA_CERTS"
      valueFrom = var.ca_certs_arn
    }
  ]
}