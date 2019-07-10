pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
    }

    stages {
        stage('Unit Tests') {
            steps {
                dir('mhs-reference-implementation') {
                    sh label: 'Installing dependencies', script: 'pipenv install --deploy --ignore-pipfile'
                    sh label: 'Running unit tests', script: 'pipenv run unittests'
                }
            }
        }

        stage('Package') {
            steps {
                sh label: 'Running Packer build', script: 'packer build pipeline/packer/mhs.json'
            }
        }

        stage('Deploy') {
            steps {
                dir('pipeline/terraform/test-environment') {
                    // TODO: Use tag name (and repo URL base?) to work out URL of container image & provide as a terraform input var
                    sh label: 'Initialising Terraform', script: 'terraform init -input=false'
                    sh label: 'Applying Terraform configuration', script: 'terraform apply -auto-approve --var cluster_id=${CLUSTER_ID} -var ecs_address=${DOCKER_REGISTRY_URL} -var task_execution_role=${TASK_EXECUTION_ROLE} -var build_id=${BUILD_TAG}'
                }
            }
        }

        stage('Integration Tests') {
            steps {
                // Wait for MHS container to fully stand up
                timeout(10) {
                    waitUntil {
                       script {
                         def r = sh script: 'curl -s -o /dev/null -w "%{http_code}" ${MHS_ADDRESS}', returnStatus: true
                         return (r != 000);
                       }
                    }
                }
                // TODO: Run actual integration tests.
                sh label: 'Ping MHS', script: 'curl ${MHS_ADDRESS}'
            }
        }
    }

    post {
        cleanup {
            dir('pipeline/terraform/test-environment') {
                    sh label: 'Destroying Terraform configuration', script: 'terraform destroy -auto-approve --var cluster_id=${CLUSTER_ID} -var ecs_address=${DOCKER_REGISTRY_URL} -var task_execution_role=${TASK_EXECUTION_ROLE} -var build_id=${BUILD_TAG}'
            }
        }
    }
}
