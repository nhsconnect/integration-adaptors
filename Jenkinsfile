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
                            -var cluster_id=${CLUSTER_ID} \
                            -var ecr_address=${DOCKER_REPOSITORY} \
                            -var scr_ecr_address=${SCR_REPOSITORY} \
                            -var task_execution_role=${TASK_EXECUTION_ROLE} \
                            -var build_id=${BUILD_TAG} \
                            -var mhs_log_level=DEBUG
                        """
                }
            }
        }

        stage('Integration Tests') {
            steps {
                dir('mhs') {
                    // Wait for MHS container to fully stand up
                    sh label: 'Ping MHS', script: 'sleep 20; curl ${MHS_ADDRESS}'
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
                        -var mhs_log_level=DEBUG
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
}
