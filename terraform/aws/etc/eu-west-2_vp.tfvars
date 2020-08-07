# Common setting for entire Env - "base" component
environment = "build2"
base_cidr_block = "10.15.0.0/16"
enable_internet_access = false
cluster_container_insights = "enabled"
docdb_instance_class = "db.r5.large"
dlt_vpc_id = "vpc-03f843c08b01876d5"
enable_dlt = true

# Settings for "nhais" component
nhais_service_minimal_count = 2
nhais_service_desired_count = 2
nhais_service_maximal_count = 4
nhais_service_target_request_count = 1200
nhais_service_container_port = 8080
nhais_service_launch_type = "FARGATE"
nhais_log_level = "DEBUG"
nhais_mesh_host = "https://mesh.vp.nhsredteam.internal.nhs.uk:8829/messageexchange/"

# Settings for "OneOneOne" component
OneOneOne_service_minimal_count = 2
OneOneOne_service_desired_count = 2
OneOneOne_service_maximal_count = 4
OneOneOne_service_target_request_count = 1200
OneOneOne_service_container_port = 8080
OneOneOne_service_launch_type = "FARGATE"
OneOneOne_log_level = "DEBUG"

# Settings for "fake_mesh" component
fake_mesh_service_launch_type = "FARGATE"
