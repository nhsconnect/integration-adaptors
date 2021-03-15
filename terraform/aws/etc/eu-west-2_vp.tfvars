# Common setting for entire Env - "base" component
environment = "vp"
base_cidr_block = "10.15.0.0/16"
enable_internet_access = false
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"
dlt_vpc_id = "vpc-03f843c08b01876d5"
enable_dlt = true
mongo_ssl_enabled = true

# Settings for "nhais" component
nhais_service_minimal_count = 2
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "INFO"
# nhais_mesh_host is also used by nhais_responder component, they must use the same MESH instance to work correctly
nhais_mesh_host = "https://mesh.vp.nhsredteam.internal.nhs.uk:8829/messageexchange/"
nhais_mesh_cert_validation = "false"
nhais_mongo_options = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tls=true"
nhais_ssl_trust_store_url = "s3://nhsd-aws-truststore/rds-truststore.jks"

# Settings for "nhais_responder" component
nhais_responder_service_minimal_count = 1
nhais_responder_service_desired_count = 1
nhais_responder_service_maximal_count = 1
nhais_responder_service_target_request_count = 1200
nhais_responder_service_container_port = 8090
nhais_responder_service_launch_type = "FARGATE"
nhais_responder_log_level = "INFO"

# Settings for "OneOneOne" component
# OneOneOne in vp will be configured to use nginx reverse proxy
OneOneOne_use_nginx_proxy = true
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
gp2gp_extract_cache_bucket_retention_period = 7
gp2gp_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
gp2gp_wiremock_container_port = 8080
gp2gp_wiremock_application_port = 8080
gp2gp_create_wiremock = true
gp2gp_create_mhs_mock = true
gp2gp_mongo_options = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tls=true"
gp2gp_ssl_trust_store_url = "s3://nhsd-aws-truststore/rds-truststore.jks"

# setting for mhs component
mhs_inbound_queue_name = "vp_inbound_queue"

# Settings for "fake_mesh" component
fake_mesh_service_launch_type = "FARGATE"
