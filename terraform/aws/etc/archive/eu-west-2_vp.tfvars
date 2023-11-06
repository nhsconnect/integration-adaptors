# Common setting for entire Env - "base" component
environment = "vp"
base_cidr_block = "10.15.0.0/16"
enable_internet_access = false
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"
dlt_vpc_id = "vpc-03f843c08b01876d5"
enable_dlt = true
mongo_ssl_enabled = true
create_testbox = true
postgres_instance_class = "db.t4g.micro"
create_postgres_db = true

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
gp2gp_mongo_options = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tls=true"
gp2gp_ssl_trust_store_url = "s3://nhsd-aws-truststore/rds-truststore.jks"
gp2gp_log_level = "INFO"
gp2gp_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
gp2gp_create_wiremock = false
gp2gp_wiremock_container_port = 8080
gp2gp_wiremock_application_port = 8080
gp2gp_create_mhs_mock = true
gp2gp_mhs_mock_build_id = "main-341-b4b28a1"
gp2gp_mock_mhs_port = 8080
gp2gp_mock_port = 8080
gp2gp_create_gpcc_mock = true
gp2gp_gpcc_mock_build_id = "main-340-4d6ff67"
gp2gp_create_gpcapi_mock = true
gp2gp_gpcapi_mock_build_id = "main-340-4d6ff67"
gp2gp_create_sdsapi_mock = true
gp2gp_sdsapi_mock_build_id ="main-340-4d6ff67"

# Settings for "gpc-consumer" component
gpc-consumer_service_minimal_count = 1
gpc-consumer_service_desired_count = 1
gpc-consumer_service_maximal_count = 1
gpc-consumer_service_target_request_count = 1200
gpc-consumer_service_container_port = 8080
gpc-consumer_service_launch_type = "FARGATE"
gpc-consumer_root_log_level = "WARN"
gpc-consumer_log_level = "INFO"
gpc-consumer_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
gpc-consumer_override_gpc_provider_url = "https://GPConnect-Win1.itblab.nic.cfh.nhs.uk"
gpc-consumer_sds_url = "https://sandbox.api.service.nhs.uk/spine-directory/"
gpc-consumer_ssp_fqdn = ""

###### FOR GPC-CONSUMER TO BE DEPLOYED IN PTL ENVIRONMENT
#gpc-consumer_include_certs = true
#secret_name_spine_client_cert = "MHS_PTL_INT_Endpoint_Cert_v3"
#secret_name_spine_client_key = "MHS_PTL_INT_Endpoint_PrivateKey_v3"
#secret_name_spine_root_ca_cert = "MHS_PTL_INT_Endpoint_CA_SHA1_SHA2"
#secret_name_spine_sub_ca_cert = "MHS_PTL_INT_Endpoint_CA_SHA1_SHA2"
#secret_name_sds_apikey = ""

# Settings for "lab-results" component
lab-results_service_minimal_count = 3
lab-results_service_desired_count = 3
lab-results_service_maximal_count = 3
lab-results_service_target_request_count = 1200
lab-results_service_container_port = 8080
lab-results_service_launch_type = "FARGATE"
lab-results_log_level = "INFO"
lab-results_mesh_host = "https://mesh.vp.nhsredteam.internal.nhs.uk:8829/messageexchange/"
lab-results_mesh_cert_validation = "false"
lab-results_mongo_options = "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tls=true"
lab-results_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
lab-results_ssl_trust_store_url = "s3://nhsd-aws-truststore/rds-truststore.jks"
lab-results_mesh_polling_cycle_minimum_interval_in_seconds = 30
lab-results_mesh_client_wakeup_interval_in_milliseconds = 10000
lab-results_mesh_polling_cycle_duration_in_seconds = 25

# setting for mhs component
mhs_inbound_queue_name = "vp_gp2gp_inbound_queue"

# Settings for "fake_mesh" component
fake_mesh_service_launch_type = "FARGATE"

# Settings for pss component
pss_service_minimal_count = 0
pss_service_desired_count = 0
pss_service_maximal_count = 0
pss_service_target_request_count = 1200
pss_service_launch_type = "FARGATE"
pss_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
create_pss_testbox = false
pss_gp2gp_translator_testbox = false
pss_gpc_facade_testbox = false
pss_gpc_api_facade_container_port = 8081
pss_gp2gp_translator_container_port = 8085
pss_mock_mhs_port = 8080
pss_service_application_port = 8080
pss_log_level = "DEBUG"
ecs_scheduler_stop_capacity = 0