
# Common setting for entire Env - "base" component
environment = "build1"
base_cidr_block = "10.11.0.0/16"
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"
docdb_tls = "disabled"

# Settings for "nhais" component
nhais_service_minimal_count = 1
nhais_service_desired_count = 1
nhais_service_maximal_count = 1
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
nhais_mesh_host = "https://msg.opentest.hscic.gov.uk/messageexchange/"
nhais_mesh_cert_validation = "true"
nhais_mongo_options = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

# Settings for "OneOneOne" component
# Name changed to "OneOneOne" from "111" because of problems with some Terraform names starting with number
OneOneOne_service_minimal_count = 2
OneOneOne_service_desired_count = 2
OneOneOne_service_maximal_count = 4
OneOneOne_service_target_request_count = 1200
OneOneOne_service_container_port = 8080
OneOneOne_service_launch_type = "FARGATE"
OneOneOne_log_level = "DEBUG"

# Settings for "gp2gp" component
gp2gp_service_desired_count = 1
gp2gp_service_minimal_count = 1
gp2gp_service_maximal_count = 1
gp2gp_service_container_port = 8080
gp2gp_service_launch_type = "FARGATE"

# Settings for "mhs" component
mhs_inbound_service_container_port = 443
mhs_inbound_service_healthcheck_port = 80
mhs_outbound_service_container_port = 80
mhs_route_service_container_port = 80
mhs_service_minimal_count = 1
mhs_service_desired_count = 1
mhs_service_maximal_count = 2
mhs_service_launch_type = "FARGATE"
mhs_log_level = "DEBUG"

mhs_outbound_forward_reliable_url = "https://192.168.128.11/reliablemessaging/forwardreliable"
mhs_route_sds_url = "ldap://192.168.128.11"
