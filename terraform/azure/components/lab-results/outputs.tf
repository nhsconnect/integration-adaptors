output lab-results_ingress {
  value = kubernetes_service.lab-results.status[0].load_balancer[0].ingress
}
