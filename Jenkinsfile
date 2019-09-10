pipeline {
    agent{
        label 'jenkins-workers'
    }

    options {
        lock('integration-test-environment')
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
        stage('SCR Web Service Unit Tests') {
            steps { dir('SCRWebService') { executeUnitTestsWithCoverage() } }
        }

        stage('Package') {
            steps {
                sh label: 'Running Inbound Packer build', script: 'packer build pipeline/packer/inbound.json'
                sh label: 'Running Outbound Packer build', script: 'packer build pipeline/packer/outbound.json'
                sh label: 'Running SCR service Packer build', script: 'packer build pipeline/packer/scr-web-service.json'
            }
        }

        stage('Deploy MHS') {
            steps {
                dir('pipeline/terraform/integration-test-environment') {
                    sh label: 'Initialising Terraform', script: """
                            terraform init \
                            -backend-config="bucket=${TF_STATE_BUCKET}" \
                            -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                            -backend-config="dynamodb_table=${TF_MHS_LOCK_TABLE_NAME}" \
                            -input=false
                        """
                    sh label: 'Destroy any existing MHS services', script: """
                            terraform destroy -auto-approve \
                            -target=aws_ecs_service.mhs_inbound_service \
                            -target=aws_ecs_service.mhs_outbound_service \
                            -var environment_id=${ENVIRONMENT_ID} \
                            -var build_id=${BUILD_TAG} \
                            -var supplier_vpc_id=${SUPPLIER_VPC_ID} \
                            -var opentest_vpc_id=${OPENTEST_VPC_ID} \
                            -var internal_root_domain=${INTERNAL_ROOT_DOMAIN} \
                            -var mhs_outbound_service_instance_count=3 \
                            -var mhs_inbound_service_instance_count=3 \
                            -var task_role_arn=${TASK_ROLE} \
                            -var execution_role_arn=${TASK_EXECUTION_ROLE} \
                            -var ecr_address=${DOCKER_REGISTRY} \
                            -var mhs_log_level=DEBUG \
                            -var mhs_outbound_http_proxy=${MHS_OUTBOUND_HTTP_PROXY} \
                            -var mhs_state_table_read_capacity=5 \
                            -var mhs_state_table_write_capacity=5 \
                            -var mhs_sync_async_table_read_capacity=5 \
                            -var mhs_sync_async_table_write_capacity=5 \
                            -var inbound_queue_host="${MHS_INBOUND_QUEUE_URL}/${MHS_INBOUND_QUEUE_NAME}" \
                            -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                            -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                            -var party_key_arn=${PARTY_KEY_ARN} \
                            -var client_cert_arn=${CLIENT_CERT_ARN} \
                            -var client_key_arn=${CLIENT_KEY_ARN} \
                            -var ca_certs_arn=${CA_CERTS_ARN} \
                            -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                            -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL}
                        """
                    sh label: 'Applying Terraform configuration', script: """
                            terraform apply -auto-approve \
                            -var environment_id=${ENVIRONMENT_ID} \
                            -var build_id=${BUILD_TAG} \
                            -var supplier_vpc_id=${SUPPLIER_VPC_ID} \
                            -var opentest_vpc_id=${OPENTEST_VPC_ID} \
                            -var internal_root_domain=${INTERNAL_ROOT_DOMAIN} \
                            -var mhs_outbound_service_instance_count=3 \
                            -var mhs_inbound_service_instance_count=3 \
                            -var task_role_arn=${TASK_ROLE} \
                            -var execution_role_arn=${TASK_EXECUTION_ROLE} \
                            -var ecr_address=${DOCKER_REGISTRY} \
                            -var mhs_log_level=DEBUG \
                            -var mhs_outbound_http_proxy=${MHS_OUTBOUND_HTTP_PROXY} \
                            -var mhs_state_table_read_capacity=5 \
                            -var mhs_state_table_write_capacity=5 \
                            -var mhs_sync_async_table_read_capacity=5 \
                            -var mhs_sync_async_table_write_capacity=5 \
                            -var inbound_queue_host="${MHS_INBOUND_QUEUE_URL}/${MHS_INBOUND_QUEUE_NAME}" \
                            -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                            -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                            -var party_key_arn=${PARTY_KEY_ARN} \
                            -var client_cert_arn=${CLIENT_CERT_ARN} \
                            -var client_key_arn=${CLIENT_KEY_ARN} \
                            -var ca_certs_arn=${CA_CERTS_ARN} \
                            -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                            -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL}
                        """
                    script {
                        env.MHS_ADDRESS = sh (
                            label: 'Obtaining outbound LB DNS name',
                            returnStdout: true,
                            script: "terraform output outbound_lb_domain_name"
                        ).trim()
                    }
                }
            }
        }

        stage('Deploy SCR') {
            steps {
                dir('pipeline/terraform/scr-test-environment') {
                    sh label: 'Initialising Terraform', script: """
                            terraform init \
                            -backend-config="bucket=${TF_STATE_BUCKET}" \
                            -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                            -backend-config="dynamodb_table=${TF_SCR_LOCK_TABLE_NAME}" \
                            -input=false
                        """
                    sh label: 'Applying Terraform configuration', script: """
                            terraform apply -auto-approve \
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
                     sh label: 'Running integration tests', script: 'pipenv run inttests'
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
