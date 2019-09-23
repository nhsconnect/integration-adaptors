pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
      ENVIRONMENT_ID = "build"
      MHS_INBOUND_QUEUE_NAME = "${ENVIRONMENT_ID}-inbound"
    }

    stages {
        stage('Build modules') {
            steps{
                dir('common'){ buildModules('Installing common dependencies') }
                dir('mhs/common'){ buildModules('Installing mhs common dependencies') }
                dir('mhs/inbound'){ buildModules('Installing inbound dependencies') }
                dir('mhs/outbound'){ buildModules('Installing outbound dependencies') }
                dir('mhs/spineroutelookup'){ buildModules('Installing route lookup dependencies')}
                dir('SCR') { buildModules('Installing SCR lib dependencies') }
                dir('SCRWebService') { buildModules('Installing SCR web service dependencies') }
            }
        }

        stage('Common Module Unit Tests') {
            steps { dir('common') { executeUnitTestsWithCoverage() } }
        }
        stage('MHS Common Unit Tests') {
            steps { dir('mhs/common') { executeUnitTestsWithCoverage() } }
        }
        stage('MHS Inbound Unit Tests') {
            steps { dir('mhs/inbound') { executeUnitTestsWithCoverage() } }
        }
        stage('MHS Outbound Unit Tests') {
            steps { dir('mhs/outbound') { executeUnitTestsWithCoverage() } }
        }
         stage('Spine Route Lookup Unit Tests') {
            steps { dir('mhs/spineroutelookup') { executeUnitTestsWithCoverage() } }
        }
        stage('SCR Library Unit Tests'){
            steps { dir('SCR')} { executeUnitTestsWithCoverage() }
        }
        stage('SCR Web Service Unit Tests') {
            steps { dir('SCRWebService') { executeUnitTestsWithCoverage() } }
        }

        stage('Package') {
            steps {
                sh label: 'Running Inbound Packer build', script: 'packer build -color=false pipeline/packer/inbound.json'
                sh label: 'Running Outbound Packer build', script: 'packer build -color=false pipeline/packer/outbound.json'
                sh label: 'Running Spine Route Lookup Packer build', script: 'packer build -color=false pipeline/packer/spineroutelookup.json'
                sh label: 'Running SCR service Packer build', script: 'packer build -color=false pipeline/packer/scr-web-service.json'
            }
        }

        stage('Run Integration Tests') {
            options {
                lock('exemplar-test-environment')
            }

            stages {
                stage('Deploy MHS') {
                    steps {
                        dir('pipeline/terraform/mhs-environment') {
                            sh label: 'Initialising Terraform', script: """
                                    terraform init \
                                    -backend-config="bucket=${TF_STATE_BUCKET}" \
                                    -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                                    -backend-config="dynamodb_table=${TF_MHS_LOCK_TABLE_NAME}" \
                                    -input=false -no-color
                                """
                            sh label: 'Applying Terraform configuration', script: """
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
                                    -var mhs_log_level=DEBUG \
                                    -var mhs_outbound_http_proxy=${MHS_OUTBOUND_HTTP_PROXY} \
                                    -var mhs_state_table_read_capacity=5 \
                                    -var mhs_state_table_write_capacity=5 \
                                    -var mhs_sync_async_table_read_capacity=5 \
                                    -var mhs_sync_async_table_write_capacity=5 \
                                    -var mhs_spine_org_code=${SPINE_ORG_CODE} \
                                    -var inbound_queue_host="${MHS_INBOUND_QUEUE_URL}/${MHS_INBOUND_QUEUE_NAME}" \
                                    -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                                    -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                                    -var party_key_arn=${PARTY_KEY_ARN} \
                                    -var client_cert_arn=${CLIENT_CERT_ARN} \
                                    -var client_key_arn=${CLIENT_KEY_ARN} \
                                    -var ca_certs_arn=${CA_CERTS_ARN} \
                                    -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                                    -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL} \
                                    -var spineroutelookup_service_sds_url=${SPINEROUTELOOKUP_SERVICE_LDAP_URL} \
                                    -var spineroutelookup_service_disable_sds_tls=${SPINEROUTELOOKUP_SERVICE_DISABLE_TLS}
                                """
                            script {
                                env.MHS_ADDRESS = sh (
                                    label: 'Obtaining outbound LB DNS name',
                                    returnStdout: true,
                                    script: "terraform output outbound_lb_domain_name"
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
                            }
                        }
                    }
                }

                stage('Deploy SCR') {
                    steps {
                        dir('pipeline/terraform/scr-environment') {
                            sh label: 'Initialising Terraform', script: """
                                    terraform init \
                                    -backend-config="bucket=${TF_STATE_BUCKET}" \
                                    -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                                    -backend-config="dynamodb_table=${TF_SCR_LOCK_TABLE_NAME}" \
                                    -input=false -no-color
                                """
                            sh label: 'Applying Terraform configuration', script: """
                                    terraform apply -no-color -auto-approve \
                                    -var environment_id=${ENVIRONMENT_ID} \
                                    -var build_id=${BUILD_TAG} \
                                    -var cluster_id=${CLUSTER_ID} \
                                    -var task_execution_role=${TASK_EXECUTION_ROLE} \
                                    -var ecr_address=${DOCKER_REGISTRY} \
                                    -var scr_log_level=DEBUG \
                                    -var scr_service_port=${SCR_SERVICE_PORT}
                                """
                        }
                    }
                }

                stage('Integration Tests') {
                    steps {
                        dir('integration-tests') {
                            sh label: 'Installing integration test dependencies', script: 'pipenv install --dev --deploy --ignore-pipfile'
                            // Wait for MHS container to fully stand up
                            timeout(2) {
                                waitUntil {
                                   script {
                                       def r = sh script: 'sleep 2; curl -o /dev/null --silent --head --write-out "%{http_code}" ${MHS_ADDRESS} || echo 1', returnStdout: true
                                       return (r == '405');
                                   }
                                }
                            }

                            // Wait for MHS load balancers to have healthy targets
                            dir('../pipeline/scripts/check-target-group-health') {
                                sh script: 'pipenv install'
                                timeout(13) {
                                    waitUntil {
                                        script {
                                            def r = sh script: 'sleep 10; AWS_DEFAULT_REGION=eu-west-2 pipenv run main ${MHS_OUTBOUND_TARGET_GROUP} ${MHS_INBOUND_TARGET_GROUP}  ${MHS_ROUTE_TARGET_GROUP}', returnStatus: true
                                            return (r == 0);
                                        }
                                    }
                                }
                            }
                            sh label: 'Running integration tests', script: 'pipenv run inttests'
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cobertura coberturaReportFile: '**/coverage.xml'
            junit '**/test-reports/*.xml'
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
