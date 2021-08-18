resource "kubernetes_deployment" "mhs-route" {
  metadata {
    name = "mhs-route"
    namespace = kubernetes_namespace.mhs.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "mhs-route"
    }
  }

  spec {

    selector {
      match_labels = {
        name = "mhs-route"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "mhs-route"
        }
      } //metadata

      spec {
        container {
          image = var.mhs-route_image
          name = "mhs-route"

          port {
            name = "container-port"
            container_port = var.mhs_route_service_container_port
            protocol = "TCP"
          } // port


          env {
            name = "MHS_DISABLE_SDS_TLS"
            value = var.mhs_route_disable_sds_tls
          }

          env {
            name = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          }

          env {
            name = "MHS_SDS_REDIS_CACHE_HOST"
            value = data.terraform_remote_state.base.outputs.redis_hostname
          }

          env {
            name = "MHS_SDS_REDIS_CACHE_PORT"
            value = data.terraform_remote_state.base.outputs.redis_non_ssl_port
          }

          env {
            name = "MHS_SDS_REDIS_DISABLE_TLS"
            value = var.mhs_route_redis_disable_tls
          }

          env {
            name = "MHS_SDS_SEARCH_BASE"
            value = var.mhs_route_sds_search_base
          }

          env {
            name = "MHS_SDS_URL"
            value = var.mhs_route_sds_url
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

        } // container
      } // spec
    } //template 
  } // spec
} // resource

