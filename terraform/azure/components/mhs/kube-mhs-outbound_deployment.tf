resource "kubernetes_deployment" "mhs-outbound" {
  metadata {
    name = "mhs-outbound"
    namespace = kubernetes_namespace.mhs.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "mhs-outbound"
    }
  }

  spec {

    selector {
      match_labels = {
        name = "mhs-outbound"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "mhs-outbound"
        }
      } //metadata

      spec {
        container {
          image = var.mhs-outbound_image
          name = "mhs-outbound"

          port {
            name = "container-port"
            container_port = var.mhs_outbound_service_container_port
            protocol = "TCP"
          } // port


          env {
            name = "MHS_FORWARD_RELIABLE_ENDPOINT_URL"
            value = var.mhs_outbound_forward_reliable_url
          }
          env {
            name = "MHS_OUTBOUND_VALIDATE_CERTIFICATE"
            value = var.mhs_outbound_validate_certificate
          }
          env {
            name = "MHS_RESYNC_INITIAL_DELAY"
            value = "0.15"
          }
          env {
            name = "MHS_RESYNC_INTERVAL"
            value = "1"
          }
          env {
            name = "MHS_RESYNC_RETRIES"
            value = "20"
          }
          env {
            name = "MHS_SPINE_ORG_CODE"
            value = var.mhs_spine_org_code
          }
          env {
            name = "MHS_SPINE_REQUEST_MAX_SIZE"
            value = "4999600"
          }
          env {
            name = "MHS_SPINE_ROUTE_LOOKUP_URL"
            value = "http://${kubernetes_service.mhs-route.metadata.0.name}:${var.mhs_service_application_port}/"
          }

          env {
            name = "MHS_OUTBOUND_SPINE_ROUTE_LOOKUP_VALIDATE_CERT"
            value = var.mhs_outbound_spineroutelookup_validate_certificate
          }


          env {
            name = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          }
          env {
            name = "MHS_DB_ENDPOINT_URL"
            value = data.terraform_remote_state.base.outputs.mongodb_connection_string[0]
          }
          env {
            name = "MHS_PERSISTENCE_ADAPTOR"
            value = "mongodb"
          }
          env {
            name = "MHS_STATE_TABLE_NAME"
            value = "${var.environment}_mhs_state"
          }
          env {
            name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
            value = "${var.environment}_mhs_sync_async"
          }

          env {
            name = "MHS_SECRET_SPINE_ROUTE_LOOKUP_CA_CERTS"
            value = var.mhs_spine_route_lookup_ca_certs
          }
          env {
            name = "MHS_SECRET_PARTY_KEY"
            value = var.mhs_party_key
          }
          env {
            name = "MHS_SECRET_CLIENT_CERT"
            value = var.mhs_client_cert
          }
          env {
            name = "MHS_SECRET_CLIENT_KEY"
            value = var.mhs_client_key
          }
          env {
            name = "MHS_SECRET_CA_CERTS"
            value = var.mhs_ca_certs
          }

          /*
          {
            name = "MHS_OUTBOUND_HTTP_PROXY"
            value = var.opentest_connected ? data.aws_instance.opentest_instance.private_ip : ""
          },
          */


        } // container
      } // spec
    } //template 
  } // spec
} // resource
