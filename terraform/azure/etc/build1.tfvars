environment = "build1"
base_cidr = "10.21.0.0/16"
base_aks_cidr = "10.21.98.0/23"
base_redis_cidr = "10.21.101.0/24"
base_testbox_cidr = "10.21.103.0/24"
base_private_dns = "build1.nhsredteam.internal.nhs.uk"

# nhais_lb_ip = "10.21.98.210"

#LAB-RESULTS CONFIGURATION
lab-results_fake_mesh_in_use     = true
lab-results_mesh_host = "https://msg.opentest.hscic.gov.uk/messageexchange/"
lab-results_mesh_cert_validation = false
lab-results_image = "nhsdev/nia-lab-results-adaptor:0.0.4"
lab-results_fake_mesh_image = "nhsdev/fake-mesh:0.2.0"
lab-results_application_port = 80
lab-results_container_port = 8080
lab-results_log_level = "INFO"
lab-results_scheduler_enabled = true
#lab-results_ssl_trust_store_url = "s3://nhsd-aws-truststore/rds-truststore.jks"

# MHS CONFIGURATION
mhs_service_application_port = 80
mhs_inbound_service_container_port = 443
mhs_outbound_service_container_port = 80
mhs_route_service_container_port = 80
mhs-inbound_image =  "nhsdev/nia-mhs-inbound:1.1.0"     # 1.0.2 / 1.1.0
mhs-outbound_image = "nhsdev/nia-mhs-outbound:1.1.0"    # 1.0.2 / 1.1.0
mhs-route_image =  "nhsdev/nia-mhs-route:1.1.0"         # 1.0.2 / 1.1.0
mhs_inbound_queue_name = "build1_mhs_inbound"
mhs_log_level = "DEBUG"
mhs_outbound_forward_reliable_url = "https://192.168.128.11/reliablemessaging/forwardreliable"
mhs_route_sds_url = "ldap://192.168.128.11"

#GP2GP CONFIGURATION
gp2gp_image = "nhsdev/nia-gp2gp-adaptor:1.2.0"          # 1.1.2 / 1.2.0
gp2gp_application_port = 80
gp2gp_container_port = 8080
gp2gp_log_level = "INFO"
# gp2gp_gpc_override_nhs_number = "9690938622"
# gp2gp_gpc_override_to_asid = "200000001329"
# gp2gp_gpc_override_from_asid = "200000001467"


#GPC-CONSUMER CONFIGURATION
gpc-consumer_image = "nhsdev/nia-gpc-consumer-adaptor:0.2.5"    # 0.1.5 / 0.2.5
gpc-consumer_include_certs = false
gpc-consumer_application_port = 80
gpc-consumer_container_port = 8080
gpc-consumer_root_log_level = "INFO"
gpc-consumer_log_level = "DEBUG"
gpc-consumer_sds_url = "https://sandbox.api.service.nhs.uk/spine-directory/"
gpc_enable_sds = "true"
gpc-consumer_ssp_fqdn = ""
