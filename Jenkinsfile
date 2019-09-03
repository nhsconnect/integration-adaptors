pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
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

        stage('Deploy') {
            steps {
                dir('pipeline/terraform/test-environment') {
                    sh label: 'Initialising Terraform', script: 'terraform init -input=false'
                    sh label: 'Applying Terraform configuration', script: """
                            terraform apply -auto-approve \
                            -var cluster_id=${CLUSTER_ID} \
                            -var ecr_address=${DOCKER_REPOSITORY} \
                            -var scr_ecr_address=${SCR_REPOSITORY} \
                            -var task_execution_role=${TASK_EXECUTION_ROLE} \
                            -var build_id=${BUILD_TAG} \
                            -var mhs_log_level=DEBUG \
                            -var mhs_state_table_name=mhs-state \
                            -var scr_log_level=DEBUG \
                            -var scr_service_port=${SCR_SERVICE_PORT} \
                            -var mhs_inbound_queue_host=${MHS_INBOUND_QUEUE_HOST} \
                            -var mhs_inbound_queue_username=${MHS_INBOUND_QUEUE_USERNAME} \
                            -var mhs_inbound_queue_password=${MHS_INBOUND_QUEUE_PASSWORD}
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
        cleanup {
            dir('pipeline/terraform/test-environment') {
                    sh label: 'Destroying Terraform configuration', script: """
                        terraform destroy -auto-approve \
                        -var cluster_id=${CLUSTER_ID} \
                        -var ecr_address=${DOCKER_REPOSITORY} \
                        -var scr_ecr_address=${SCR_REPOSITORY} \
                        -var task_execution_role=${TASK_EXECUTION_ROLE} \
                        -var build_id=${BUILD_TAG} \
                        -var mhs_log_level=DEBUG \
                        -var mhs_state_table_name=mhs-state \
                        -var scr_log_level=DEBUG \
                        -var scr_service_port=${SCR_SERVICE_PORT} \
                        -var mhs_inbound_queue_host=${MHS_INBOUND_QUEUE_HOST} \
                        -var mhs_inbound_queue_username=${MHS_INBOUND_QUEUE_USERNAME} \
                        -var mhs_inbound_queue_password=${MHS_INBOUND_QUEUE_PASSWORD}
                     """
            }
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
