locals {
  # variables common for all three adapters
  environment_variables = concat(var.mhs_environment_variables,[
    {
      name = "MHS_LOG_LEVEL"
      value = var.mhs_log_level
    },
    {
      name = "MHS_STATE_TABLE_NAME"
      value = "mhs_state"
    },
    {
      name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
      value = "mhs_sync_async"
    },
    {
      name = "MHS_PERSISTENCE_ADAPTOR"
      value = "mongodb"
    },
    {
      name = "MHS_DB_ENDPOINT_URL"
      value = data.terraform_remote_state.base.outputs.docdb_cluster_endpoint
    },
  ])

  outbound_variables = concat(local.environment_variables, [
    {
      name = "MHS_SPINE_ROUTE_LOOKUP_URL"
      value = "https://${aws_route53_record.mhs_route_lb_record.name}"
    },
    {
      name = "MHS_OUTBOUND_VALIDATE_CERTIFICATE"
      value = var.mhs_outbound_validate_certificate
    },
    {
      name = "MHS_OUTBOUND_SPINE_ROUTE_LOOKUP_VALIDATE_CERT"
      value = var.mhs_outbound_spineroutelookup_verify_certificate
    }
  ])

  inbound_variables = concat(local.environment_variables, [])
  route_variables = concat(local.environment_variables, [])
}

/*

    {
      name = "MHS_RESYNC_RETRIES"
      value = var.mhs_resynchroniser_max_retries
    },
    {
      name = "MHS_RESYNC_INTERVAL"
      value = var.mhs_resynchroniser_interval
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
    },

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



*/
/*
     - env:
        - name: MHS_INBOUND_QUEUE_BROKERS
          valueFrom:
            secretKeyRef:
              name: mhs-queue
              key: broker
        - name: MHS_INBOUND_QUEUE_NAME
          valueFrom:
            secretKeyRef:
              name: mhs-queue
              key: queue
        - name: MHS_SECRET_INBOUND_QUEUE_USERNAME
          valueFrom:
            secretKeyRef:
              name: mhs-queue
              key: username
        - name: MHS_SECRET_INBOUND_QUEUE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mhs-queue
              key: password
        - name: MHS_LOG_LEVEL
          value: DEBUG
        - name: MHS_STATE_TABLE_NAME
          value: mhs_state
        - name: MHS_SYNC_ASYNC_STATE_TABLE_NAME
          value: sync_async_state
        - name: MHS_SECRET_PARTY_KEY
          valueFrom:
            secretKeyRef:
              name: mhs-partykey
              key: partyKey
        - name: MHS_SECRET_CLIENT_CERT
          valueFrom:
            secretKeyRef:
              name: mhs-client-cert
              key: tls.crt
        - name: MHS_SECRET_CLIENT_KEY	
          valueFrom:
            secretKeyRef:
              name: mhs-client-cert
              key: tls.key
        - name: MHS_SECRET_CA_CERTS
          valueFrom:
            secretKeyRef:
              name: mhs-ca-certs
              key: ca-certs
        - name: MHS_DB_ENDPOINT_URL
          valueFrom:
            secretKeyRef:
              name: mhs-database
              key: connectionString
        - name: MHS_PERSISTENCE_ADAPTOR
          value: mongodb
        - name: MHS_INBOUND_USE_SSL
          value: "false"
        - name: MHS_INBOUND_QUEUE_MESSAGE_TTL_IN_SECONDS
          value: "0"
        - name: SERVICE_PORTS
          value: 443,80
        - name: TCP_PORTS
          value: "443"



*/