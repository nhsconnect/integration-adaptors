resource "kubernetes_deployment" "nhais" {
  metadata {
    name = "nhais"
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "nhais"
    }
  }

  spec {
    replicas = var.nhais_replicas

    selector {
      match_labels = {
        name = "nhais"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "nhais"
        }
      } //metadata

      spec {
        container {
          image = var.nhais_image
          name = "nhais"

          port {
            name = "container-port"
            container_port = "${var.nhais_container_port}"
            protocol = "TCP"
          } // port

          env {
            name = "NHAIS_AMQP_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.nhais_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }

          env {
              name = "NHAIS_AMQP_USERNAME"
              value = azurerm_servicebus_namespace_authorization_rule.nhais_servicebus_ar.name
          }

          env {
              name = "NHAIS_AMQP_PASSWORD"
              value = azurerm_servicebus_namespace_authorization_rule.nhais_servicebus_ar.primary_key
          }

          env {
              name = "NHAIS_MESH_OUTBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.nhais_mesh_outbound_queue.name
          }

          env {
              name = "NHAIS_MESH_INBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.nhais_mesh_inbound_queue.name
          }

          env {
              name = "NHAIS_GP_SYSTEM_INBOUND_QUEUE_NAME"
              value = azurerm_servicebus_queue.nhais_gp_inbound_queue.name
          }

          env {
              name = "NHAIS_MONGO_HOST"
              value = data.terraform_remote_state.base.outputs.mongodb_hostname
          }

          env {
              name = "NHAIS_MONGO_PORT"
              value = data.terraform_remote_state.base.outputs.mongodb_port
          }

          env {
              name = "NHAIS_MONGO_USERNAME"
              value = data.terraform_remote_state.base.outputs.mongodb_username
          }

          env {
              name = "NHAIS_MONGO_PASSWORD"
              value = data.terraform_remote_state.base.outputs.mongodb_password
          }

          env {
              name = "NHAIS_MONGO_OPTIONS"
              value = "ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@${data.terraform_remote_state.base.outputs.mongodb_username}"
          }

          env {
              name = "NHAIS_COSMOS_DB_ENABLED"
              value = "true"
          }

          env {
              name = "NHAIS_MESH_MAILBOX_ID"
              value = var.nhais_mesh_mailbox_id
          }

          env {
              name = "NHAIS_MESH_MAILBOX_PASSWORD"
              value = var.nhais_mesh_mailbox_password
          }

          env {
              name = "NHAIS_MESH_SHARED_KEY"
              value = var.nhais_mesh_shared_key
          }

          env {
              name = "NHAIS_MESH_HOST"
              value = var.fake_mesh_in_use ? "https://${kubernetes_service.fake_mesh[0].metadata.0.name}:${var.fake_mesh_application_port}/messageexchange/" : var.nhais_mesh_host
          }

          env {
              name = "NHAIS_MESH_CERT_VALIDATION"
              value = var.nhais_mesh_cert_validation
          }

          env {
              name = "NHAIS_MESH_SUB_CA"
              value = var.nhais_mesh_sub_ca
          }

          env {
              name = "NHAIS_MESH_ENDPOINT_CERT"
              value = var.nhais_mesh_endpoint_cert
          }

          env {
              name = "NHAIS_MESH_ENDPOINT_PRIVATE_KEY"
              value = var.nhais_mesh_endpoint_private_key
          }

          env {
              name = "NHAIS_MESH_RECIPIENT_MAILBOX_ID_MAPPINGS"
              value = var.nhais_mesh_recipient_mailbox_id_mappings
          }

          env {
              name = "NHAIS_MESH_POLLING_CYCLE_MINIMUM_INTERVAL_IN_SECONDS"
              value = var.nhais_mesh_polling_cycle_minimum_interval_in_seconds
          }

          env {
              name = "NHAIS_MESH_CLIENT_WAKEUP_INTERVAL_IN_MILLISECONDS"
              value = var.nhais_mesh_client_wakeup_interval_in_miliseconds
          }

          env {
              name = "NHAIS_SCHEDULER_ENABLED"
              value = var.nhais_scheduler_enabled
          }
        } // container
      } // spec
    } //template 
  } // spec
} // resource
