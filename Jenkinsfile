pipeline {
    agent {
        label 'jenkins-workers'
    }

    environment {
        BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER} ${GIT_COMMIT}'
        BUILD_TAG_LOWER = sh label: 'Lowercase build tag', returnStdout: true, script: "echo -n ${BUILD_TAG} | tr '[:upper:]' '[:lower:]'"
        ENVIRONMENT_ID = "build"
        MHS_INBOUND_QUEUE_NAME = "${ENVIRONMENT_ID}-inbound"
    }

    stages {
        stage('Build modules') {
            parallel {
                stage('Common') {
                    stages {
                        stage('Build') {
                            steps {
                                dir('common') {
                                    buildModules('Installing common dependencies')
                                }
                            }
                        }
                        stage('Unit test') {
                            steps {
                                dir('common') {
                                    executeUnitTestsWithCoverage()
                                }
                            }
                        }
                    }
                }
                stage('MHS Common') {
                    stages {
                        stage('Build') {
                            steps {
                                dir('mhs/common') {
                                    buildModules('Installing mhs common dependencies')
                                }
                            }
                        }
                        stage('Unit test') {
                            steps {
                                dir('mhs/common') {
                                    executeUnitTestsWithCoverage()
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Build MHS') {
            parallel {
                stage('Inbound') {
                    stages {
                        stage('Build') {
                            steps {
                                dir('mhs/inbound') {
                                    buildModules('Installing inbound dependencies')
                                }
                            }
                        }
                        stage('Unit test') {
                            steps {
                                dir('mhs/inbound') {
                                    executeUnitTestsWithCoverage()
                                }
                            }
                        }
                        stage('Build image') {
                            steps {
                                script {
                                    sh label: 'Building inbound image', script: "docker build -t local/mhs-inbound:${BUILD_TAG} -f dockers/mhs/inbound/Dockerfile ."
                                }
                            }
                        }
                        stage('Push image') {
                            steps {
                                script {
                                    sh label: 'Pushing inbound image', script: "packer build -color=false pipeline/packer/inbound-push.json"
                                }
                            }
                        }
                    }
                }
                stage('Outbound') {
                    stages {
                        stage('Installing outbound dependencies') {
                            steps {
                                dir('mhs/outbound') {
                                    buildModules('Installing outbound dependencies')
                                    executeUnitTestsWithCoverage()
                                }
                                script {
                                    sh label: 'Building outbound iamge', script: "docker build -t local/mhs-outbound:${BUILD_TAG} -f dockers/mhs/outbound/Dockerfile ."
                                }
                                script {
                                    sh label: 'Pushing outbound image', script: "packer build -color=false pipeline/packer/outbound-push.json"
                                }
                            }
                        }
                    }
                }
                stage('Spine Route Lookup') {
                    stages {
                        stage('Installing route lookup dependencies') {
                            steps {
                                dir('mhs/spineroutelookup') {
                                    buildModules('Installing route lookup dependencies')
                                    executeUnitTestsWithCoverage()
                                }
                                script {
                                    sh label: 'Building spine route lookup image', script: "docker build -t local/mhs-spineroutelookup:${BUILD_TAG} -f dockers/mhs/spineroutelookup/Dockerfile ."
                                }
                                script {
                                    sh label: 'Pushing spine route lookup image', script: "packer build -color=false pipeline/packer/spineroutelookup-push.json"
                                }
                            }
                        }
                    }
                }
                stage('SCR') {
                    stages {
                        stage('Installing SCR web service dependencies') {
                            steps {
                                dir('SCRWebService') {
                                    buildModules('Installing SCR web service dependencies')
                                    executeUnitTestsWithCoverage()
                                }
                                script{
                                    sh label: 'Building SCR web service image', script: "docker build -t local/scr-web-service:${BUILD_TAG} -f dockers/scr-web-service/Dockerfile ."
                                }
                                script {
                                    sh label: 'Oushing SCR web service image', script: "packer build -color=false pipeline/packer/scr-web-service-push.json"
                                }
                            }
                        }
                    }
                }
            }
        }

        // stage('Module Unit Tests') {
        //     parallel {
        //         stage('Run Common') {
        //             stages {
        //                 stage('Common Module Unit Tests') {
        //                     steps { dir('common') { executeUnitTestsWithCoverage() } }
        //                 }
        //             }
        //         }
        //         stage('Run MHS Common ') {
        //             stages {
        //                 stage('MHS Common Unit Tests') {
        //                     steps { dir('mhs/common') { executeUnitTestsWithCoverage() } }
        //                 }
        //             }
        //         }
        //         stage('Run MHS Inbound') {
        //             stages {
        //                 stage('MHS Inbound Unit Tests') {
        //                     steps { dir('mhs/inbound') { executeUnitTestsWithCoverage() } }
        //                 }
        //             }
        //         }
        //         stage('Run MHS Outbound') {
        //             stages {
        //                 stage('MHS Outbound Unit Tests') {
        //                     steps {
        //                         dir('mhs/outbound') {
        //                             executeUnitTestsWithCoverage()
        //                             sh label: 'Check API docs can be generated', script: 'pipenv run generate-openapi-docs > /dev/null'
        //                         }
        //                     }
        //                 }
        //             }
        //         }
        //         stage('Run Spine Route Lookup') {
        //             stages {
        //                 stage('Spine Route Lookup Unit Tests') {
        //                     steps { dir('mhs/spineroutelookup') { executeUnitTestsWithCoverage() } }
        //                 }
        //             }
        //         }
        //         stage('Run SCR Web Service') {
        //             stages {
        //                 stage('SCR Web Service Unit Tests') {
        //                     steps { dir('SCRWebService') { executeUnitTestsWithCoverage() } }
        //                 }
        //             }
        //         }
        //     }
        // }

        // stage('Build images') {
            // parallel {
                // stage('Inbound') {
                //     stages {
                //         stage('Package Inbound') {
                //             steps {
                //                 script {
                //                     sh label: 'Building inbound image', script: "docker build -t local/mhs-inbound:${BUILD_TAG} -f dockers/mhs/inbound/Dockerfile ."
                //                 }
                //                 script {
                //                     sh label: 'Pushing inbound image', script: "packer build -color=false pipeline/packer/inbound-push.json"
                //                 }
                //             }
                //         }
                //     }
                // }
                // stage('Outbound') {
                //     stages {
                //         stage('Package Outbound') {
                //             steps {
                //                 script {
                //                     sh label: 'Building outbound iamge', script: "docker build -t local/mhs-outbound:${BUILD_TAG} -f dockers/mhs/outbound/Dockerfile ."
                //                 }
                //                 script {
                //                     sh label: 'Pushing outbound image', script: "packer build -color=false pipeline/packer/outbound-push.json"
                //                 }
                //             }
                //         }
                //     }
                // }
                // stage('Spine Route Lookup') {
                //     stages {
                //         stage('Package Spine Route Lookup') {
                //             steps {
                //                 script {
                //                     sh label: 'Building spine route lookup image', script: "docker build -t local/mhs-spineroutelookup:${BUILD_TAG} -f dockers/mhs/spineroutelookup/Dockerfile ."
                //                 }
                //                 script {
                //                     sh label: 'Pushing spine route lookup image', script: "packer build -color=false pipeline/packer/spineroutelookup-push.json"
                //                 }
                //             }
                //         }
                //     }
                // }
                // stage('SCR Module Package') {
                //     stages {
                //         stage('Package SCR Web Service') {
                //             steps {
                //                 script{
                //                     sh label: 'Building SCR web service image', script: "docker build -t local/scr-web-service:${BUILD_TAG} -f dockers/scr-web-service/Dockerfile ."
                //                 }
                //                 script {
                //                     sh label: 'Oushing SCR web service image', script: "packer build -color=false pipeline/packer/scr-web-service-push.json"
                //                 }
                //             }
                //         }
                //     }
                // }
            // }
        // }

        stage('Component and Integration Tests') {
            parallel {
                stage('Component Tests') {
                    options {
                        lock('local-docker-compose-environment')
                    }
                    stages {
                        stage('Deploy component locally') {
                            steps {
                                sh label: 'Setup component test environment', script: './integration-tests/setup_component_test_env.sh'
                                sh label: 'Starting docker images', script: '''
                                    docker-compose -f docker-compose.yml -f docker-compose.component.override.yml down -v
                                    docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p custom_network down -v
                                    . ./component-test-source.sh
                                    docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} up --build -d'''
                            }
                        }
                        stage('Run Component Tests') {
                            steps {
                                sh label: 'Running component tests', script: '''
                             docker build -t componenttest:$BUILD_TAG -f ./component-test.Dockerfile .
                             docker run --rm --network "${BUILD_TAG_LOWER}_default" \
                                --env "MHS_ADDRESS=http://outbound" \
                                --env "AWS_ACCESS_KEY_ID=test" \
                                --env "AWS_SECRET_ACCESS_KEY=test" \
                                --env "MHS_DYNAMODB_ENDPOINT_URL=http://dynamodb:8000" \
                                --env "FAKE_SPINE_ADDRESS=http://fakespine" \
                                --env "MHS_INBOUND_QUEUE_URL=http://rabbitmq:5672" \
                                --env "SCR_ADDRESS=http://scradaptor" \
                                componenttest:$BUILD_TAG
                        '''
                            }
                        }
                    }
                    post {
                        always {
                            sh label: 'Docker compose logs', script: 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} logs'
                            sh label: 'Docker compose down', script: 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} down -v'
                        }
                    }
                }

                stage('Integration Tests') {
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
                                    -var route_ca_certs_arn=${ROUTE_CA_CERTS_ARN} \
                                    -var outbound_alb_certificate_arn=${OUTBOUND_ALB_CERT_ARN} \
                                    -var route_alb_certificate_arn=${ROUTE_ALB_CERT_ARN} \
                                    -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                                    -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL} \
                                    -var spineroutelookup_service_sds_url=${SPINEROUTELOOKUP_SERVICE_LDAP_URL} \
                                    -var spineroutelookup_service_search_base=${SPINEROUTELOOKUP_SERVICE_SEARCH_BASE} \
                                    -var spineroutelookup_service_disable_sds_tls=${SPINEROUTELOOKUP_SERVICE_DISABLE_TLS} \
                                    -var elasticache_node_type="cache.t2.micro" \
                                    -var mhs_forward_reliable_endpoint_url=${MHS_FORWARD_RELIABLE_ENDPOINT_URL}
                                """
                                    script {
                                        env.MHS_ADDRESS = sh(
                                                label: 'Obtaining outbound LB DNS name',
                                                returnStdout: true,
                                                script: "echo \"https://\$(terraform output outbound_lb_domain_name)\""
                                        ).trim()
                                        env.MHS_OUTBOUND_TARGET_GROUP = sh(
                                                label: 'Obtaining outbound LB target group ARN',
                                                returnStdout: true,
                                                script: "terraform output outbound_lb_target_group_arn"
                                        ).trim()
                                        env.MHS_INBOUND_TARGET_GROUP = sh(
                                                label: 'Obtaining inbound LB target group ARN',
                                                returnStdout: true,
                                                script: "terraform output inbound_lb_target_group_arn"
                                        ).trim()
                                        env.MHS_ROUTE_TARGET_GROUP = sh(
                                                label: 'Obtaining route LB target group ARN',
                                                returnStdout: true,
                                                script: "terraform output route_lb_target_group_arn"
                                        ).trim()
                                        env.MHS_DYNAMODB_TABLE_NAME = sh(
                                                label: 'Obtaining the dynamodb table name used for the MHS state',
                                                returnStdout: true,
                                                script: "terraform output mhs_state_table_name"
                                        ).trim()
                                        env.MHS_SYNC_ASYNC_TABLE_NAME = sh(
                                                label: 'Obtaining the dynamodb table name used for the MHS sync/async state',
                                                returnStdout: true,
                                                script: "terraform output mhs_sync_async_table_name"
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
                                    -var scr_service_port=${SCR_SERVICE_PORT} \
                                    -var scr_mhs_address=${MHS_ADDRESS} \
                                    -var scr_mhs_ca_certs_arn=${OUTBOUND_CA_CERTS_ARN}
                                """
                                }
                            }
                        }

                        stage('Run integration tests') {
                            steps {
                                dir('integration-tests/integration_tests') {
                                    sh label: 'Installing integration test dependencies', script: 'pipenv install --dev --deploy --ignore-pipfile'

                                    // Wait for MHS load balancers to have healthy targets
                                    dir('../../pipeline/scripts/check-target-group-health') {
                                        sh script: 'pipenv install'

                                        timeout(13) {
                                            waitUntil {
                                                script {
                                                    def r = sh label: 'Waiting for load balancer...', script: 'sleep 3; AWS_DEFAULT_REGION=eu-west-2 pipenv run main ${MHS_OUTBOUND_TARGET_GROUP} ${MHS_INBOUND_TARGET_GROUP}  ${MHS_ROUTE_TARGET_GROUP}', returnStatus: true
                                                    return (r == 0)
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
        }
    }

    post {
        always {
            cobertura coberturaReportFile: '**/coverage.xml'
            junit '**/test-reports/*.xml'
            sh 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} down -v'
            sh 'docker volume prune --force'
            // Prune Docker images for current CI build.
            // Note that the * in the glob patterns doesn't match /
            // Test child dependant image removal first
            sh 'docker image rm -f $(docker images "*/*:*${BUILD_TAG}" -q) $(docker images "*/*/*:*${BUILD_TAG}" -q) || true'
            sh label: 'List docker containers', script: 'docker ps'
            sh label: 'List all docker containers', script: 'docker ps -a'
            sh label: 'List all docker images', script: 'docker images'
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

void buildDockerImage(String action, String repository, String dockerfile) {
    sh label: action, script: "docker build -t " + repository + ":${BUILD_TAG} -f " + dockerFile + " ."
}

