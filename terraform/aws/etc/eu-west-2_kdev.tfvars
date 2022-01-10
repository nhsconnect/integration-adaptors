# Common setting for entire Env - "base" component
environment = "kdev"
base_cidr_block = "10.17.0.0/16"
cluster_container_insights = "enabled"
docdb_instance_class = "db.t3.medium"
mongo_ssl_enabled = true
enable_internet_access = "true"
create_opentest_instance = false
postgres_instance_class = "db.t4g.micro"
create_postgres_db = true

# Settings for "pss" component
pss_service_minimal_count = 1
pss_service_desired_count = 1
pss_service_maximal_count = 1
pss_service_target_request_count = 1200
pss_service_launch_type = "FARGATE"
pss_logs_datetime_format = "%Y-%m-%d %H:%M:%S%L"
pss_gp2gp_translator_testbox = false
pss_gpc_facade_testbox = false
pss_gpc_api_facade_container_port = 8081
pss_gp2gp_translator_container_port = 8085
pss_mock_mhs_port = 8080
pss_service_application_port = 8080
pss_log_level = "DEBUG"