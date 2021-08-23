output mhs-inbound_queue_name {
  value = azurerm_servicebus_queue.mhs_inbound_queue.name
}

output mhs-outbound_url {
  value = "http://${kubernetes_service.mhs-outbound.metadata.0.name}:${var.mhs_service_application_port}/"
}

output mhs-route_url {
  value = "http://${kubernetes_service.mhs-route.metadata.0.name}:${var.mhs_service_application_port}/"
}

output mhs-outbound_ingress {
  value = kubernetes_service.mhs-outbound.status[0].load_balancer[0].ingress
}
output mhs-route_ingress {
  value = kubernetes_service.mhs-route.status[0].load_balancer[0].ingress
}