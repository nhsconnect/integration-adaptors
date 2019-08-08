pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
    }

    stages {
        stage('Common Module Unit Tests') {
            steps {
                dir('common') {
                    executeUnitTestsWithCoverage()
               }
            }
        }

        stage('MHS Unit Tests') {
            steps {
                dir('mhs') {
                    executeUnitTestsWithCoverage()
               }
            }
        }
        stage('SCR Web Service Unit Tests') {
            steps {
                dir('SCRWebService') {
                    executeUnitTestsWithCoverage()
               }
            }
        }

        stage('Package') {
            steps {
                sh label: 'Running MHS Packer build', script: 'packer build pipeline/packer/mhs.json'
                sh label: 'Running SCR service Packer build', script: 'packer build pipeline/packer/scr-web-service.json'
            }
        }

        stage('Deploy') {
            steps {
                dir('pipeline/terraform/test-environment') {
                    sh label: 'Initialising Terraform', script: 'terraform init -input=false'
                    sh label: 'Applying Terraform configuration', script: """
                            terraform apply -auto-approve \
                            -var cluster_id=${CLUSTER_ID_2} \
                            -var ecr_address=${DOCKER_REPOSITORY} \
                            -var scr_ecr_address=${SCR_REPOSITORY} \
                            -var task_execution_role=${TASK_EXECUTION_ROLE} \
                            -var build_id=${BUILD_TAG} \
                            -var mhs_log_level=DEBUG \
                            -var scr_log_level=DEBUG \
                            -var scr_service_port=${SCR_SERVICE_PORT} \
                            -var queue_security_group_id=${QUEUE_SG_ID} \
                            -var environment=${ENVIRONMENT} 
                        """
                }
            }
        }

        stage('MHS Integration Tests') {
            steps {
                dir('mhs') {
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

        stage('SCR Service Integration Tests') {
            steps {
                dir('SCRWebService') {
                     timeout(2) {
                        waitUntil {
                           script {
                               def r = sh script: 'sleep 2; curl -o /dev/null --silent --head --write-out "%{http_code}" ${MHS_ADDRESS}:${SCR_SERVICE_PORT} || echo 1', returnStdout: true
                               return (r == '404');
                           }
                        }
                     }

                    sh label: 'Running SCR integration tests', script: 'pipenv run inttests'
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
                        -var scr_log_level=DEBUG \
                        -var scr_service_port=${SCR_SERVICE_PORT} \
                        -var queue_security_group_id=${QUEUE_SG_ID} \
                        -var environment=${ENVIRONMENT} 
                     """
            }
        }
    }
}

void executeUnitTestsWithCoverage() {
    sh label: 'Installing dependencies', script: 'pipenv install --dev --deploy --ignore-pipfile'
    sh label: 'Running unit tests', script: 'pipenv run unittests-cov'
    sh label: 'Displaying code coverage report', script: 'pipenv run coverage-report'
    sh label: 'Exporting code coverage report', script: 'pipenv run coverage-report-xml'
    sh label: 'Running SonarQube analysis', script: "sonar-scanner -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONAR_TOKEN}"
}
