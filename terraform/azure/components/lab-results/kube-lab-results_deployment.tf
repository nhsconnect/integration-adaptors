resource "kubernetes_deployment" "lab-results" {
  metadata {
    name = "lab-results"
    namespace = kubernetes_namespace.lab-results.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "lab-results"
    }
  }

  spec {
    replicas = var.lab-results_replicas

    selector {
      match_labels = {
        name = "lab-results"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "lab-results"
        }
      } //metadata

      spec {
        container {
          image = var.lab-results_image
          name = "lab-results"

          port {
            name = "container-port"
            container_port = var.lab-results_container_port
            protocol = "TCP"
          } // port


          env {
              name = "LAB_RESULTS_MONGO_USERNAME"
              value = data.terraform_remote_state.base.outputs.mongodb_username
          }

          env {
              name = "LAB_RESULTS_MONGO_PASSWORD"
              value = data.terraform_remote_state.base.outputs.mongodb_password
          }

          env {
              name = "LAB_RESULTS_MONGO_OPTIONS"
              value = "ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@${data.terraform_remote_state.base.outputs.mongodb_username}"
          }

          env {
              name = "LAB_RESULTS_MONGO_DATABASE_NAME"
              value = "lab-results"
          }

          env {
              name = "LAB_RESULTS_MONGO_HOST"
              value = data.terraform_remote_state.base.outputs.mongodb_hostname
          }

          env {
              name = "LAB_RESULTS_MONGO_PORT"
              value = data.terraform_remote_state.base.outputs.mongodb_port
          }

          env {
              name = "LAB_RESULTS_MONGO_AUTO_INDEX_CREATION"
              value = true
          }

          env {
              name = "LAB_RESULTS_MONGO_TTL"
              value = "P30D"
          }

          env {
              name = "LAB_RESULTS_COSMOS_DB_ENABLED"
              value = "true"
          }

          env {
              name = "LAB_RESULTS_LOGGING_LEVEL"
              value = var.lab-results_log_level
          }

          env {
              name = "LAB_RESULTS_MESH_MAILBOX_ID"
              value = var.lab-results_mesh_mailbox_id
          }

          env {
              name = "LAB_RESULTS_MESH_MAILBOX_PASSWORD"
              value = var.lab-results_mesh_mailbox_password
          }

          env {
              name = "LAB_RESULTS_MESH_SHARED_KEY"
              value = var.lab-results_mesh_shared_key
          }
          env {
              name = "LAB_RESULTS_MESH_SUB_CA"
              value = var.lab-results_mesh_sub_ca
          }

          env {
              name = "LAB_RESULTS_MESH_ENDPOINT_CERT"
              value = var.lab-results_mesh_endpoint_cert
          }

          env {
              name = "LAB_RESULTS_MESH_ENDPOINT_PRIVATE_KEY"
              value = var.lab-results_mesh_endpoint_private_key
          }

          env {
              name = "LAB_RESULTS_MESH_RECIPIENT_MAILBOX_ID_MAPPINGS"
              value = var.lab-results_mesh_recipient_mailbox_id_mappings
          }

          env {
              name = "LAB_RESULTS_SSL_TRUST_STORE_PASSWORD"
              value = var.lab-results_ssl_trust_store_password
          }


          env {
              name = "LAB_RESULTS_AMQP_USERNAME"
              value = azurerm_servicebus_namespace_authorization_rule.lab-results_servicebus_ar.name
          }

          env {
              name = "LAB_RESULTS_AMQP_PASSWORD"
              value = azurerm_servicebus_namespace_authorization_rule.lab-results_servicebus_ar.primary_key
          }

          env {
            name = "LAB_RESULTS_AMQP_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.lab-results_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }
 
          env {
              name = "LAB_RESULTS_AMQP_MAX_REDELIVERIES"
              value = var.lab-results_amqp_max_redeliveries
          }

          env {
              name = "LAB_RESULTS_AMQP_RETRY_DELAY"
              value = var.lab-results_amqp_retry_delay
          }

          env {
              name = "LAB_RESULTS_MESH_OUTBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.lab-results_mesh_outbound_queue.name
          }

          env {
              name = "LAB_RESULTS_MESH_INBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.lab-results_mesh_inbound_queue.name
          }

          env {
              name = "LAB_RESULTS_GP_OUTBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.lab-results_gp_outbound_queue.name
          }

          env {
              name = "LAB_RESULTS_MESH_HOST"
              value = var.lab-results_fake_mesh_in_use ? "https://${kubernetes_service.fake_mesh[0].metadata.0.name}:${var.lab-results_fake_mesh_application_port}/messageexchange/" : var.lab-results_mesh_host
          }

          env {
              name = "LAB_RESULTS_MESH_CERT_VALIDATION"
              value = var.lab-results_mesh_cert_validation
          }

          env {
            name  = "LAB_RESULTS_OUTBOUND_SERVER_PORT"
            value = var.lab-results_container_port
          }

          env {
            name  = "LAB_RESULTS_MESH_API_HTTP_PROXY"
            value = ""
          }

          env {
              name = "LAB_RESULTS_MESH_POLLING_CYCLE_MINIMUM_INTERVAL_IN_SECONDS"
              value = var.lab-results_mesh_polling_cycle_minimum_interval_in_seconds
          }

          env {
              name = "LAB_RESULTS_MESH_CLIENT_WAKEUP_INTERVAL_IN_MILLISECONDS"
              value = var.lab-results_mesh_client_wakeup_interval_in_miliseconds
          }

          env {
              name = "LAB_RESULTS_MESH_POLLING_CYCLE_DURATION_IN_SECONDS"
              value = var.lab-results_mesh_polling_cycle_duration_in_seconds
          }

          env {
              name = "LAB_RESULTS_SCHEDULER_ENABLED"
              value = var.lab-results_scheduler_enabled
          }

          env {
              name = "LAB_RESULTS_SSL_TRUST_STORE_URL"
              value = var.lab-results_ssl_trust_store_url
          }

          env {
              name = "LAB_RESULTS_LOGGING_APPENDER"
              value = "TEXT"
          }




        } // container
      } // spec
    } //template 
  } // spec
} // resource
