output nhais_ingress {
  value = kubernetes_service.nhais.status[0].load_balancer[0].ingress
}
