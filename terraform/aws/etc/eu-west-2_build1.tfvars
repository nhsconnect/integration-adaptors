
# Common setting for entire Env - "base" component
environment = "build1"
base_cidr_block = "10.11.0.0/16"
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"

# Settings for "nhais" component
nhais_service_minimal_count = 1
nhais_service_desired_count = 1
nhais_service_maximal_count = 1
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
# TODO: Determine correct OpenTest MESH details for build1
nhais_mesh_host = "https://localhost:8829/messageexchange/"

# Settings for "OneOneOne" component
# Name changed to "OneOneOne" from "111" because of problems with some Terraform names starting with number
OneOneOne_service_minimal_count = 2
OneOneOne_service_desired_count = 2
OneOneOne_service_maximal_count = 4
OneOneOne_service_target_request_count = 1200
OneOneOne_service_container_port = 8080
OneOneOne_service_launch_type = "FARGATE"
OneOneOne_log_level = "DEBUG"
