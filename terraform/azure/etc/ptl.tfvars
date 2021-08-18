environment          = "ptl"
base_cidr            = "10.22.0.0/16"
ptl_cidr             = "172.28.65.0/24"
ptl_connected        = true
fake_mesh_in_use     = false
base_aks_cidr        = "172.28.65.128/25"
base_ptl_next_hop    = "172.17.166.116"
base_ptl_prefixes    = [ "172.17.0.0/16", "155.231.231.0/29", "10.239.0.0/16" ]
base_ptl_dns_servers = [ "155.231.231.1", "155.231.231.2" ]
base_redis_cidr      = "10.22.101.0/24"
base_testbox_cidr    = "172.28.65.0/26"

nhais_mesh_host = "https://msg.int.spine2.ncrs.nhs.uk/messageexchange/"
nhais_mesh_cert_validation = true

#LAB-RESULTS CONFIGURATION
lab-results_fake_mesh_in_use     = false
lab-results_mesh_host = "https://msg.int.spine2.ncrs.nhs.uk/messageexchange/"
lab-results_mesh_cert_validation = "true"
lab-results_image = "nhsdev/nia-lab-results-adaptor:0.0.4"
lab-results_application_port = 80
lab-results_container_port = 8080
lab-results_log_level = "INFO"
lab-results_scheduler_enabled = true

# MHS CONFIGURATION
mhs_service_application_port = 80
mhs_inbound_service_container_port = 443
mhs_outbound_service_container_port = 80
mhs_route_service_container_port = 80
mhs-inbound_image =  "nhsdev/nia-mhs-inbound:1.0.2"
mhs-outbound_image = "nhsdev/nia-mhs-outbound:1.0.2"
mhs-route_image =  "nhsdev/nia-mhs-route:1.0.2"
mhs_inbound_queue_name = "ptl_mhs_inbound"
mhs_log_level = "INFO"
mhs_outbound_forward_reliable_url =  "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest"
mhs_route_sds_url = "ldaps://ldap.nis1.national.ncrs.nhs.uk"
