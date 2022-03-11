resource "kubernetes_deployment" "pss-gp2gp-translator" {
  metadata {
    name = "pss-gp2gp-translator"
    namespace = kubernetes_namespace.pss.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "pss-gp2gp-translator"
    }
  }

  spec {
    replicas = var.pss_replicas

    selector {
      match_labels = {
        name = "pss-gp2gp-translator"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "pss-gp2gp-translator"
        }
      } //metadata

      spec {
        container {
          image = var.pss_image
          name = "pss-gp2gp-translator"

          port {
            name = "container-port"
            container_port = var.pss_gp2gp_translator_container_port
            protocol = "TCP"
          } // port

          env {
            name = "PSS_AMQP_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.pss_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }

          env {
              name = "PSS_AMQP_USERNAME"
              value = azurerm_servicebus_namespace_authorization_rule.pss_servicebus_ar.name
          }

          env {
              name = "PSS_AMQP_PASSWORD"
              value = azurerm_servicebus_namespace_authorization_rule.pss_servicebus_ar.primary_key
          }

          env {
              name = "PSS_LOGGING_LEVEL"
              value = var.pss_log_level
          }
 
          env {
              name = "PSS_AMQP_MAX_REDELIVERIES"
              value = var.pss_amqp_max_redeliveries
          }

          env {
              name = "PS_DB_URL"
              value = "jdbc:${data.terraform_remote_state.base.outputs.postgres_instance_connection_string}"
          }

          env {
            name  = "PS_QUEUE_NAME"
            value = azurerm_servicebus_queue.pss_tasks_queue.name
          }


# PSS GP2GP Translator Adapter Settings

          env {
            name  = "GP2GP_TRANSLATOR_SERVER_PORT"
            value = var.pss_gp2gp_translator_container_port
          }

          env {
             name = "MHS_QUEUE_NAME"
             value = "${var.environment}-pss-mhs-queue"
          }

          env {
            name = "MHS_AMQP_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.pss_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }

          env {
             name = "MHS_AMQP_MAX_REDELIVERIES"
             value = var.pss_amqp_max_redeliveries
          }

        } // container
      } // spec
    } //template 
  } // spec
} // resource
