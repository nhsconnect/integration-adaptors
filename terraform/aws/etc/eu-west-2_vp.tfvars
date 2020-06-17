environment = "vp"
base_cidr_block = "10.12.0.0/16"

nhais_service_minimal_count = 1
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
cluster_container_insights = "enabled"
build_id = "develop-28-1d81ddf"
docdb_instance_class = "db.r5.large"
dlt_vpc_id = "vpc-03f843c08b01876d5"
enable_dlt = true
