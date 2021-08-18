resource "kubernetes_deployment" "mhs-inbound" {
  metadata {
    name = "mhs-inbound"
    namespace = kubernetes_namespace.mhs.metadata.0.name


    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "mhs-inbound"
    }
  }

  spec {

    selector {
      match_labels = {
        name = "mhs-inbound"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "mhs-inbound"
        }
      } //metadata

      spec {
        container {
          image = var.mhs-inbound_image
          name = "mhs-inbound"

          port {
            name = "container-port"
            container_port = var.mhs_inbound_service_container_port
            protocol = "TCP"
          } // port

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
            name = "MHS_INBOUND_QUEUE_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.mhs_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }
          env {
              name = "MHS_INBOUND_QUEUE_USERNAME"
              value = azurerm_servicebus_namespace_authorization_rule.mhs_servicebus_ar.name
          }
          env {
              name = "MHS_INBOUND_QUEUE_PASSWORD"
              value = azurerm_servicebus_namespace_authorization_rule.mhs_servicebus_ar.primary_key
          }
          env {
            name = "MHS_INBOUND_QUEUE_NAME"
            value = azurerm_servicebus_queue.mhs_inbound_queue.name
          }
          env {
            name = "MHS_INBOUND_USE_SSL"
            value = var.mhs_inbound_use_ssl
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
          env {
            name = "MHS_SECRET_SPINE_ROUTE_LOOKUP_CA_CERTS"
            value = var.mhs_spine_route_lookup_ca_certs
          }

        } // container
      } // spec
    } //template 
  } // spec
} // resource
