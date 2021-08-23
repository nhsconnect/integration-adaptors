resource "kubernetes_deployment" "gp2gp" {
  metadata {
    name = "gp2gp"
    namespace = kubernetes_namespace.gp2gp.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "gp2gp"
    }
  }

  spec {
    replicas = var.gp2gp_replicas

    selector {
      match_labels = {
        name = "gp2gp"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "gp2gp"
        }
      } //metadata

      spec {
        container {
          image = var.gp2gp_image
          name = "gp2gp"

          port {
            name = "container-port"
            container_port = var.gp2gp_container_port
            protocol = "TCP"
          } // port

          env {
              name = "GP2GP_COSMOS_DB_ENABLED"
              value = "true"
          }

          env {
              name = "GP2GP_MONGO_HOST"
              value = data.terraform_remote_state.base.outputs.mongodb_hostname
          }

          env {
              name = "GP2GP_MONGO_PORT"
              value = data.terraform_remote_state.base.outputs.mongodb_port
          }

          env {
              name = "GP2GP_MONGO_OPTIONS"
              value = "ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@${data.terraform_remote_state.base.outputs.mongodb_username}"
          }

          env {
              name = "GP2GP_MONGO_DATABASE_NAME"
              value = "gp2gp"
          }

          env {
              name = "GP2GP_MONGO_USERNAME"
              value = data.terraform_remote_state.base.outputs.mongodb_username
          }

          env {
              name = "GP2GP_MONGO_PASSWORD"
              value = data.terraform_remote_state.base.outputs.mongodb_password
          }

          env {
              name = "GP2GP_MONGO_TTL"
              value = "P30D"
          }

          env {
            name = "GP2GP_AMQP_BROKERS"
            value = "amqps://${replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.gp2gp_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")}:5671/?sasl=plain"
          }

          env {
              name = "GP2GP_AMQP_USERNAME"
              value = azurerm_servicebus_namespace_authorization_rule.gp2gp_servicebus_ar.name
          }

          env {
              name = "GP2GP_AMQP_PASSWORD"
              value = azurerm_servicebus_namespace_authorization_rule.gp2gp_servicebus_ar.primary_key
          }
 
          env {
              name = "GP2GP_AMQP_MAX_REDELIVERIES"
              value = var.gp2gp_amqp_max_redeliveries
          }

          env {
              name = "GP2GP_AMQP_RETRY_DELAY"
              value = var.gp2gp_amqp_retry_delay
          }

          env {
              name = "GP2GP_STORAGE_TYPE"
              value = "Azure"
          }

          env {
              name = "GP2GP_STORAGE_CONTAINER_NAME"
              value = azurerm_storage_container.gp2gp_bucket_container.name
          }

          env {
              name = "GP2GP_AZURE_STORAGE_CONNECTION_STRING"
              value = data.terraform_remote_state.account.outputs.storage_account_connection_string
          }

          env {
              name = "GP2GP_LOGGING_LEVEL"
              value = var.gp2gp_log_level
          }

          env {
            name  = "GP2GP_TASK_QUEUE"
            value = azurerm_servicebus_queue.gp2gp_tasks_queue.name
          }

          env {
            name = "GP2GP_GPC_OVERRIDE_NHS_NUMBER"
            value = var.gp2gp_gpc_override_nhs_number
          }
          
          env {
            name = "GP2GP_GPC_OVERRIDE_TO_ASID"
            value = var.gp2gp_gpc_override_to_asid
          }
          
          env {
            name = "GP2GP_GPC_OVERRIDE_FROM_ASID"
            value = var.gp2gp_gpc_override_from_asid
          }

          env {
            name = "GP2GP_GPC_GET_STRUCTURED_ENDPOINT"
            value = var.gp2gp_gpc_get_structured_endpoint
          }

          env {
            name = "GP2GP_GPC_GET_DOCUMENT_ENDPOINT"
            value = var.gp2gp_gpc_get_document_endpoint
          }

          env {
            name = "GP2GP_GPC_HOST"
            value = var.gp2gp_gpc_host
          }

          env {
            name = "GP2GP_GPC_GET_URL"
            value = "http://${kubernetes_service.gpc-consumer.metadata.0.name}:${var.gpc-consumer_application_port}/B82617/STU3/1/gpconnect"
          }

          env {
            name  = "GP2GP_GPC_CONSUMER_URL"
            value = "http://${kubernetes_service.gpc-consumer.metadata.0.name}:${var.gpc-consumer_application_port}"
          }

# MHS Adapter Settings
          env {
            name  = "GP2GP_MHS_INBOUND_QUEUE"
            value = data.terraform_remote_state.mhs.outputs.mhs-inbound_queue_name
          }

          env {
            name = "GP2GP_MHS_OUTBOUND_URL"
            value = "http://${data.terraform_remote_state.mhs.outputs.mhs-outbound_ingress[0].ip}"           
          }

        } // container
      } // spec
    } //template 
  } // spec
} // resource
