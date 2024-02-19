resource "kubernetes_deployment" "gpc-consumer" {
  metadata {
    name = "gp2gp-gpc-consumer"
    namespace = kubernetes_namespace.gp2gp.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "gp2gp-gpc-consumer"
    }
  }

  spec {
    replicas = var.gp2gp_replicas

    selector {
      match_labels = {
        name = "gp2gp-gpc-consumer"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "gp2gp-gpc-consumer"
        }
      } //metadata

      spec {
        container {
          image = var.gpc-consumer_image
          name = "gp2gp-gpc-consumer"

          port {
            name = "container-port"
            container_port = var.gpc-consumer_container_port
            protocol = "TCP"
          } // port

          env {
            name = "GPC_CONSUMER_SPINE_CLIENT_CERT"
            value = var.gpc-consumer_spine_client_cert
          }

          env {
            name = "GPC_CONSUMER_SPINE_CLIENT_KEY"
            value = var.gpc-consumer_spine_client_key
          }

          env {
            name = "GPC_CONSUMER_SPINE_ROOT_CA_CERT"
            value = var.gpc-consumer_spine_root_ca_cert
          }
          
          env {
            name = "GPC_CONSUMER_SPINE_SUB_CA_CERT"
            value = var.gpc-consumer_spine_sub_ca_cert
          }
          
          env {
            name = "GPC_CONSUMER_SDS_APIKEY"
            value = var.gpc-consumer_sds_apikey
          }

          env {
            name  = "GPC_CONSUMER_SERVER_PORT"
            value = var.gpc-consumer_container_port
          }

          env {
            name  = "GPC_CONSUMER_ROOT_LOGGING_LEVEL"
            value = var.gpc-consumer_root_log_level
          }
          
          env {
            name  = "GPC_CONSUMER_LOGGING_LEVEL"
            value = var.gpc-consumer_log_level
          }
          
          env {
            name  = "GPC_CONSUMER_URL"
            value = "http://${kubernetes_service.gpc-consumer.metadata.0.name}:${var.gpc-consumer_application_port}"
          }

          env {
            name  = "GPC_CONSUMER_GPC_GET_URL"
            value = "https://GPConnect-Win1.itblab.nic.cfh.nhs.uk"
          }
          
          env {
            name  = "GPC_CONSUMER_SDS_URL"
            value = var.gpc-consumer_sds_url
          }

          env {
            name  = "GPC_SUPPLIER_ODS_CODE"
            value = var.gpc-consumer_supplier_ods_code
          }

          env {
            name  = "GPC_CONSUMER_SSP_FQDN"
            value = var.gpc-consumer_ssp_fqdn
          }
          
          env {
            name  = "GPC_ENABLE_SDS"
            value = var.gpc_enable_sds
          }

        } // container
      } // spec
    } //template 
  } // spec
} // resource
