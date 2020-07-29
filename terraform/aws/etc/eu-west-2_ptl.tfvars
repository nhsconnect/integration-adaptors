# Common setting for entire Env - "base" component
environment = "ptl"
base_cidr_block = "10.16.0.0/16"
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"
ptl_connected = true

# Settings for "nhais" component
nhais_service_minimal_count = 1
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
nhais_mesh_host = "https://msg.int.spine2.ncrs.nhs.uk/messageexchange/"

# Settings for "OneOneOne" component
# Name changed to "OneOneOne" from "111" because of problems with some Terraform names starting with number
OneOneOne_service_minimal_count = 2
OneOneOne_service_desired_count = 2
OneOneOne_service_maximal_count = 4
OneOneOne_service_target_request_count = 1200
OneOneOne_service_container_port = 8080
OneOneOne_service_launch_type = "FARGATE"
OneOneOne_log_level = "DEBUG"

# Settings for "fake_mesh" component
fake_mesh_service_launch_type = "FARGATE"