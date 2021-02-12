output fake_mesh_ingress {
  value = kubernetes_service.fake_mesh[0].status[0].load_balancer[0].ingress
}

output nhais_ingress {
  value = kubernetes_service.nhais.status[0].load_balancer[0].ingress
}
