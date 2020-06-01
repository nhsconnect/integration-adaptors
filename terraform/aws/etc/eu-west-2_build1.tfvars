environment = "build1"
base_cidr_block = "10.11.0.0/16"

nhais_service_minimal_count = 1
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
cluster_container_insights = "enabled"
build_id = "develop-2-6659f4e"
docdb_instance_class = "db.r5.large"
