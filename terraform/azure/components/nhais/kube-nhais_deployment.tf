
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   labels:
#     app: nhais
#   name: nhais
# spec:
#   replicas: 1
#   selector:
#     matchLabels:
#       app: nhais
#   template:
#     metadata:
#       labels:
#         app: nhais
#     spec:
#       containers:
#       - image: nhsdev/nia-nhais-adaptor:1.4.1
#         name: nhais
#         ports:
#         - containerPort: 8080
#         env:

#         - name: NHAIS_MONGO_HOST
#           value: nhais.mongo.cosmos.azure.com
#         - name: NHAIS_MONGO_PORT
#           value: "10255"
#         - name: NHAIS_MONGO_USERNAME
#           value: nhais
#         - name: NHAIS_MONGO_PASSWORD
#           value: "CHANGE_ME"
#         - name: NHAIS_MONGO_OPTIONS
#           value: "ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@michalsc@&retrywrites=false"
#         - name: NHAIS_COSMOS_DB_ENABLED
#           value: "true"
#         - name: NHAIS_MESH_MAILBOX_ID
#           value: gp_mailbox
#         - name: NHAIS_MESH_MAILBOX_PASSWORD
#           value: password
#         - name: NHAIS_MESH_SHARED_KEY
#           value: SharedKey
#         - name: NHAIS_MESH_HOST
#           value: https://fake-mesh:8829/messageexchange/
#         - name: NHAIS_MESH_CERT_VALIDATION
#           value: "false"
#         - name: NHAIS_MESH_ENDPOINT_CERT
#           value: |
#            -------CERT----------
#         - name: NHAIS_MESH_ENDPOINT_PRIVATE_KEY
#           value: |
#             -------CERT--------
#         - name: NHAIS_MESH_RECIPIENT_MAILBOX_ID_MAPPINGS
#           value: |
#             XX11=nhais_mailbox
#             TES5=nhais_mailbox
#             YY21=nhais_mailbox
#             KC01=nhais_mailbox
#             WHI5=nhais_mailbox
#             SO01=nhais_mailbox
#             UNY5=nhais_mailbox
#             BAA1=nhais_mailbox
#         - name: NHAIS_MESH_POLLING_CYCLE_MINIMUM_INTERVAL_IN_SECONDS
#           value: "300"
#         - name: NHAIS_MESH_CLIENT_WAKEUP_INTERVAL_IN_MILLISECONDS
#           value: "60000"
#         - name: NHAIS_SCHEDULER_ENABLED
#           value: "true"

resource "kubernetes_deployment" "nhais" {
  metadata {
    name = "${local.resource_prefix}-deployment"
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = "${local.resource_prefix}-deployment"
    }
  }

  spec {
    replicas = var.nhais_replicas

    selector {
      match_labels = {
        Component = "nhais"
        Environment = var.environment
      }
    } // selector

    template {
      metadata {
        labels = {
          Project = var.project
          Environment = var.environment
          Component = var.component
          Name = "${local.resource_prefix}-deployment"
        }
      } //metadata

      spec {
        container {
          image = var.nhais_image
          name = local.resource_prefix

          port {
            name = "container-port"
            container_port = "${var.nhais_container_port}"
            protocol = "TCP"
          } // port

          env {
            name = "NHAIS_AMQP_BROKERS"
            value = replace(replace(split(";", azurerm_servicebus_namespace_authorization_rule.nhais_servicebus_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")
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
              value = data.terraform_remote_state.base.outputs.mongodb_connection_string[0]
          }

          # env {
          #     name = "NHAIS_MONGO_PORT"
          #     value = ""
          # }

          # env {
          #     name = "NHAIS_MONGO_USERNAME"
          #     value = ""
          # }

          # env {
          #     name = "NHAIS_MONGO_PASSWORD"
          #     value = ""
          # }

          # env {
          #     name = "NHAIS_MONGO_OPTIONS"
          #     value = ""
          # }

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
              value = var.nhais_mesh_host
          }

          env {
              name = "NHAIS_MESH_CERT_VALIDATION"
              value = var.nhais_mesh_cert_validation
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
