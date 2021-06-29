environment = "build1"
base_cidr = "10.21.0.0/16"
base_aks_cidr = "10.21.98.0/23"
base_redis_cidr = "10.21.101.0/24"
base_testbox_cidr = "10.21.103.0/24"

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
