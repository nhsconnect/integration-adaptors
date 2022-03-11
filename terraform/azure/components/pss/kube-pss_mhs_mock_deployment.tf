resource "kubernetes_deployment" "pss-mock-mhs" {
  metadata {
    name = "pss-mock-mhs"
    namespace = kubernetes_namespace.pss.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "pss-mock-mhs"
    }
  }

  spec {
    replicas = var.pss_replicas

    selector {
      match_labels = {
        name = "pss-mock-mhs"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "pss-mock-mhs"
        }
      } //metadata

      spec {
        container {
          image = var.pss_image
          name = "pss-mock-mhs"

          port {
            name = "container-port"
            container_port = var.pss_mock_mhs_port
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

        } // container
      } // spec
    } //template 
  } // spec
} // resource
