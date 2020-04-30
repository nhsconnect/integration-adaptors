pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
        BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER} ${GIT_COMMIT}'
        BUILD_TAG_LOWER = sh label: 'Lowercase build tag', returnStdout: true, script: "echo -n ${BUILD_TAG} | tr '[:upper:]' '[:lower:]'"
        ENVIRONMENT_ID = "ptl"
        MHS_INBOUND_QUEUE_NAME = "${ENVIRONMENT_ID}-inbound"
    }

    stages {
        stage('Build MHS') {
            parallel {
                stage('Inbound Push image') {
                    steps {
                        script {
                            sh label: 'Pushing inbound image', script: "packer build -color=false pipeline/packer/inbound.json"
                        }
                    }
                }
                stage('Outbound Push image') {
                    steps {
                        script {
                            sh label: 'Pushing outbound image', script: "packer build -color=false pipeline/packer/outbound.json"
                        }
                    }
                }
                stage('Route Push image') {
                    steps {
                        script {
                            sh label: 'Pushing spine route lookup image', script: "packer build -color=false pipeline/packer/spineroutelookup.json"
                        }
                    }
                }
            }
        }
        stage('Deploy MHS') {
            steps {
                dir('pipeline/terraform/mhs-environment') {
                    sh label: 'Initialising Terraform', script: """
                            terraform init \
                            -backend-config="bucket=${TF_STATE_BUCKET}" \
                            -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                            -backend-config="key=${ENVIRONMENT_ID}-mhs.tfstate" \
                            -backend-config="dynamodb_table=${ENVIRONMENT_ID}-${TF_MHS_LOCK_TABLE_NAME}" \
                            -input=false -no-color
                        """
                    sh label: 'Applying Terraform configuration, part 1', script: """
                            terraform apply -no-color -auto-approve \
                            -var environment_id=${ENVIRONMENT_ID} \
                            -var build_id=${BUILD_TAG} \
                            -var supplier_vpc_id=${SUPPLIER_VPC_ID} \
                            -var opentest_vpc_id=${OPENTEST_VPC_ID} \
                            -var internal_root_domain=${INTERNAL_ROOT_DOMAIN} \
                            -var mhs_outbound_service_minimum_instance_count=3 \
                            -var mhs_outbound_service_maximum_instance_count=9 \
                            -var mhs_inbound_service_minimum_instance_count=3 \
                            -var mhs_inbound_service_maximum_instance_count=9 \
                            -var mhs_route_service_minimum_instance_count=3 \
                            -var mhs_route_service_maximum_instance_count=9 \
                            -var task_role_arn=${TASK_ROLE} \
                            -var execution_role_arn=${TASK_EXECUTION_ROLE} \
                            -var task_scaling_role_arn=${TASK_SCALING_ROLE} \
                            -var ecr_address=${DOCKER_REGISTRY} \
                            -var mhs_outbound_validate_certificate=${MHS_OUTBOUND_VALIDATE_CERTIFICATE} \
                            -var mhs_log_level=DEBUG \
                            -var mhs_outbound_http_proxy=${MHS_OUTBOUND_HTTP_PROXY} \
                            -var mhs_state_table_read_capacity=5 \
                            -var mhs_state_table_write_capacity=5 \
                            -var mhs_sync_async_table_read_capacity=5 \
                            -var mhs_sync_async_table_write_capacity=5 \
                            -var mhs_spine_org_code=${SPINE_ORG_CODE} \
                            -var inbound_queue_brokers="${MHS_INBOUND_QUEUE_BROKERS}" \
                            -var inbound_queue_name="${MHS_INBOUND_QUEUE_NAME}" \
                            -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                            -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                            -var party_key_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_PARTY_KEY-FbOTJn \
                            -var client_cert_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_Cert-AhPyol \
                            -var client_key_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PLT_INT_Endpoint_PrivateKey-Fu1jb6 \
                            -var ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_CA_valid_till_may_2022-XJup7p \
                            -var route_ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_CA_valid_till_may_2022-XJup7p \
                            -var outbound_alb_certificate_arn=${OUTBOUND_ALB_CERT_ARN} \
                            -var route_alb_certificate_arn=${ROUTE_ALB_CERT_ARN} \
                            -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                            -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL} \
                            -var spineroutelookup_service_sds_url="ldaps://ldap.nis1.national.ncrs.nhs.uk" \
                            -var spineroutelookup_service_search_base=${SPINEROUTELOOKUP_SERVICE_SEARCH_BASE} \
                            -var spineroutelookup_service_disable_sds_tls="False" \
                            -var elasticache_node_type="cache.t2.micro" \
                            -var mhs_forward_reliable_endpoint_url="https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest"
                        """
                        script {
                            println("Wait 2 minutes between applies")
                            sleep(120)
                        }
                        //  terraform plan -no-color -auto-approve \
                        sh label: 'Applying Terraform configuration, part 2', script: """
                            terraform plan -no-color -auto-approve \
                            -var environment_id=${ENVIRONMENT_ID} \
                            -var build_id=${BUILD_TAG} \
                            -var supplier_vpc_id=${SUPPLIER_VPC_ID} \
                            -var opentest_vpc_id=${OPENTEST_VPC_ID} \
                            -var internal_root_domain=${INTERNAL_ROOT_DOMAIN} \
                            -var mhs_outbound_service_minimum_instance_count=3 \
                            -var mhs_outbound_service_maximum_instance_count=9 \
                            -var mhs_inbound_service_minimum_instance_count=3 \
                            -var mhs_inbound_service_maximum_instance_count=9 \
                            -var mhs_route_service_minimum_instance_count=3 \
                            -var mhs_route_service_maximum_instance_count=9 \
                            -var task_role_arn=${TASK_ROLE} \
                            -var execution_role_arn=${TASK_EXECUTION_ROLE} \
                            -var task_scaling_role_arn=${TASK_SCALING_ROLE} \
                            -var ecr_address=${DOCKER_REGISTRY} \
                            -var mhs_outbound_validate_certificate=${MHS_OUTBOUND_VALIDATE_CERTIFICATE} \
                            -var mhs_log_level=DEBUG \
                            -var mhs_outbound_http_proxy=${MHS_OUTBOUND_HTTP_PROXY} \
                            -var mhs_state_table_read_capacity=5 \
                            -var mhs_state_table_write_capacity=5 \
                            -var mhs_sync_async_table_read_capacity=5 \
                            -var mhs_sync_async_table_write_capacity=5 \
                            -var mhs_spine_org_code=${SPINE_ORG_CODE} \
                            -var inbound_queue_brokers="${MHS_INBOUND_QUEUE_BROKERS}" \
                            -var inbound_queue_name="${MHS_INBOUND_QUEUE_NAME}" \
                            -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                            -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                            -var party_key_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_PARTY_KEY-FbOTJn \
                            -var client_cert_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_Cert-AhPyol \
                            -var client_key_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PLT_INT_Endpoint_PrivateKey-Fu1jb6 \
                            -var ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_CA_valid_till_may_2022-XJup7p \
                            -var route_ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:MHS_PTL_INT_Endpoint_CA_valid_till_may_2022-XJup7p \
                            -var outbound_alb_certificate_arn=${OUTBOUND_ALB_CERT_ARN} \
                            -var route_alb_certificate_arn=${ROUTE_ALB_CERT_ARN} \
                            -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                            -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL} \
                            -var spineroutelookup_service_sds_url="ldaps://ldap.nis1.national.ncrs.nhs.uk" \
                            -var spineroutelookup_service_search_base=${SPINEROUTELOOKUP_SERVICE_SEARCH_BASE} \
                            -var spineroutelookup_service_disable_sds_tls="False" \
                            -var elasticache_node_type="cache.t2.micro" \
                            -var mhs_forward_reliable_endpoint_url="https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest" \
                            -var dhcp_options_in_use="nhs"
                        """                   
                    script {
                        env.MHS_ADDRESS = sh (
                            label: 'Obtaining outbound LB DNS name',
                            returnStdout: true,
                            script: "echo \"https://\$(terraform output outbound_lb_domain_name)\""
                        ).trim()
                        env.MHS_OUTBOUND_TARGET_GROUP = sh (
                            label: 'Obtaining outbound LB target group ARN',
                            returnStdout: true,
                            script: "terraform output outbound_lb_target_group_arn"
                        ).trim()
                        env.MHS_INBOUND_TARGET_GROUP = sh (
                            label: 'Obtaining inbound LB target group ARN',
                            returnStdout: true,
                            script: "terraform output inbound_lb_target_group_arn"
                        ).trim()
                        env.MHS_ROUTE_TARGET_GROUP = sh (
                            label: 'Obtaining route LB target group ARN',
                            returnStdout: true,
                            script: "terraform output route_lb_target_group_arn"
                        ).trim()
                        env.MHS_DYNAMODB_TABLE_NAME = sh (
                            label: 'Obtaining the dynamodb table name used for the MHS state',
                            returnStdout: true,
                            script: "terraform output mhs_state_table_name"
                        ).trim()
                        env.MHS_SYNC_ASYNC_TABLE_NAME = sh (
                            label: 'Obtaining the dynamodb table name used for the MHS sync/async state',
                            returnStdout: true,
                            script: "terraform output mhs_sync_async_table_name"
                        ).trim()
                    }
                }
            }
        }
   }

    post {
        always {
//             cobertura coberturaReportFile: '**/coverage.xml'
//             junit '**/test-reports/*.xml'
            sh 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} down -v'
            sh 'docker volume prune --force'
            // Prune Docker images for current CI build.
            // Note that the * in the glob patterns doesn't match /
            sh 'docker image rm -f $(docker images "*/*:*${BUILD_TAG}" -q) $(docker images "*/*/*:*${BUILD_TAG}" -q) || true'
        }
    }
}

void executeUnitTestsWithCoverage() {
    sh label: 'Running unit tests', script: 'pipenv run unittests-cov'
    sh label: 'Displaying code coverage report', script: 'pipenv run coverage-report'
    sh label: 'Exporting code coverage report', script: 'pipenv run coverage-report-xml'
    sh label: 'Running SonarQube analysis', script: "sonar-scanner -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONAR_TOKEN}"
}

void buildModules(String action) {
    sh label: action, script: 'pipenv install --dev --deploy --ignore-pipfile'
}
