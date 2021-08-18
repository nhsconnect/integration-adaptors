output mhs-inbound_queue_name {
  value = azurerm_servicebus_queue.mhs_inbound_queue.name
}

output mhs-outbound_url {
  value = "http://${kubernetes_service.mhs-outbound.metadata.0.name}:${var.mhs_service_application_port}/"
}

output mhs-route_url {
  value = "http://${kubernetes_service.mhs-route.metadata.0.name}:${var.mhs_service_application_port}/"
}
