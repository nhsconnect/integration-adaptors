provider "kubernetes" {}

resource "kubernetes_namespace" "mhs-adaptor" {
  metadata {
    name = "${var.namespace}"
  }
}
### Inbound ###
resource "kubernetes_pod" "inbound" {
  metadata {
    name = "inbound"

    labels = {
      name = "inbound"
    }

    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    container {
      image = "nhsdev/nia-mhs-inbound:latest"
      name  = "inbound"
    }
  }
}

resource "kubernetes_service" "inbound" {
  metadata {
    name      = "inbound"
    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    selector = {
      name = "${kubernetes_pod.inbound.metadata.0.labels.name}"
    }

    port {
      port        = 80
      target_port = 80
   }
    # port {
    #   port        = 443
    #   target_port = 443
    # }

  #   type = "LoadBalancer"
  }
}

### Outbound ####
resource "kubernetes_pod" "outbound" {
  metadata {
    name = "outbound"

    labels = {
      name = "outbound"
    }

    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    container {
      image = "nhsdev/nia-mhs-outbound:latest"
      name  = "outbound"
    }
  }
}

resource "kubernetes_service" "outbound" {
  metadata {
    name      = "outbound"
    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    selector = {
      name = "${kubernetes_pod.outbound.metadata.0.labels.name}"
    }

    port {
      port        = 80
      target_port = 80
    }
  }
}

### Route ####
resource "kubernetes_pod" "route" {
  metadata {
    name = "route"

    labels = {
      name = "route"
    }

    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    container {
      image = "nhsdev/nia-mhs-route:latest"
      name  = "route"
    }
  }
}

resource "kubernetes_service" "route" {
  metadata {
    name      = "route"
    namespace = "${kubernetes_namespace.mhs-adaptor.metadata.0.name}"
  }

  spec {
    selector = {
      name = "${kubernetes_pod.route.metadata.0.labels.name}"
    }

    port {
      port        = 80
      target_port = 80
    }

  }
}