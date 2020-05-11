pipeline {
    agent{
        label 'jenkins-workers'
    }

    environment {
        BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER} ${GIT_COMMIT}'
        BUILD_TAG_LOWER = sh label: 'Lowercase build tag', returnStdout: true, script: "echo -n ${BUILD_TAG} | tr '[:upper:]' '[:lower:]'"
        ENVIRONMENT_ID = "vp-testing"
        MHS_INBOUND_QUEUE_NAME = "${ENVIRONMENT_ID}-inbound"

    }

    stages {
//         stage('Build & test common') {
//             steps {
//                 dir('common') {
//                     buildModules('Installing common dependencies')
//                     executeUnitTestsWithCoverage()
//                 }
//             }
//         }
//         stage('Build & test MHS Common') {
//             steps {
//                 dir('mhs/common') {
//                     buildModules('Installing mhs common dependencies')
//                     executeUnitTestsWithCoverage()
//                 }
//             }
//         }

        stage('Build MHS') {
            parallel {
                stage('Inbound') {
                    stages {
//                         stage('Build') {
//                             steps {
//                                 dir('mhs/inbound') {
//                                     buildModules('Installing inbound dependencies')
//                                 }
//                             }
//                         }
//                         stage('Unit test') {
//                             steps {
//                                 dir('mhs/inbound') {
//                                     executeUnitTestsWithCoverage()
//                                 }
//                             }
//                         }
                        stage('Push image') {
                            steps {
                                script {
                                    sh label: 'Pushing inbound image', script: "packer build -color=false pipeline/packer/inbound.json"
                                }
                            }
                        }
                    }
                }
                stage('Outbound') {
                    stages {
//                         stage('Build') {
//                             steps {
//                                 dir('mhs/outbound') {
//                                     buildModules('Installing outbound dependencies')
//                                 }
//                             }
//                         }
//                         stage('Unit test') {
//                             steps {
//                                 dir('mhs/outbound') {
//                                     executeUnitTestsWithCoverage()
//                                 }
//                             }
//                         }
//                         stage('Check documentation') {
//                             steps {
//                                 dir('mhs/outbound') {
//                                     sh label: 'Check API docs can be generated', script: 'pipenv run generate-openapi-docs > /dev/null'
//                                 }
//                             }
//                         }
                        stage('Push image') {
                            steps {
                                script {
                                    sh label: 'Pushing outbound image', script: "packer build -color=false pipeline/packer/outbound.json"
                                }
                            }
                        }
                    }
                }
                stage('Route') {
                    stages {
//                         stage('Build') {
//                             steps {
//                                 dir('mhs/spineroutelookup') {
//                                     buildModules('Installing route lookup dependencies')
//                                 }
//                             }
//                         }
//                         stage('Unit test') {
//                             steps {
//                                 dir('mhs/spineroutelookup') {
//                                     executeUnitTestsWithCoverage()
//                                 }
//                             }
//                         }
                        stage('Push image') {
                            steps {
                                script {
                                    sh label: 'Pushing spine route lookup image', script: "packer build -color=false pipeline/packer/spineroutelookup.json"
                                }
                            }
                        }
                    }
                }
            }
        }

//         stage('Test') {
//             // NIAD-189: Parallel component and integration tests disabled due to intermittent build failures
//             //parallel {
//             stages {
//                 stage('Run Component Tests') {
//                     options {
//                         lock('local-docker-compose-environment')
//                     }
//                     stages {
//                         stage('Deploy component locally') {
//                             steps {
//                                 sh label: 'Setup component test environment', script: './integration-tests/setup_component_test_env.sh'
//                                 sh label: 'Start containers', script: '''
//                                     docker-compose -f docker-compose.yml -f docker-compose.component.override.yml down -v
//                                     docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p custom_network down -v
//                                     . ./component-test-source.sh
//                                     docker-compose -f docker-compose.yml -f docker-compose.component.override.yml build
//                                     docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} up -d'''
//                             }
//                         }
//                         stage('Component Tests') {
//                             steps {
//                                 sh label: 'Run component tests', script: '''
//                                     docker build -t local/mhs-componenttest:$BUILD_TAG -f ./component-test.Dockerfile .
//                                     docker run --rm --network "${BUILD_TAG_LOWER}_default" \
//                                         --env "MHS_ADDRESS=http://outbound" \
//                                         --env "AWS_ACCESS_KEY_ID=test" \
//                                         --env "AWS_SECRET_ACCESS_KEY=test" \
//                                         --env "MHS_DYNAMODB_ENDPOINT_URL=http://dynamodb:8000" \
//                                         --env "FAKE_SPINE_ADDRESS=http://fakespine" \
//                                         --env "MHS_INBOUND_QUEUE_BROKERS=amqp://rabbitmq:5672" \
//                                         --env "MHS_INBOUND_QUEUE_NAME=inbound" \
//                                         --env "SCR_ADDRESS=http://scradaptor" \
//                                         local/mhs-componenttest:$BUILD_TAG
//                                 '''
//                             }
//                         }
//                     }
//                     post {
//                         always {
//                             sh label: 'Docker status', script: 'docker ps --all'
//                             sh label: 'Dump container logs to files', script: '''
//                                 mkdir logs
//                                 docker logs ${BUILD_TAG_LOWER}_route_1 > logs/route.log
//                                 docker logs ${BUILD_TAG_LOWER}_outbound_1 > logs/outbound.log
//                                 docker logs ${BUILD_TAG_LOWER}_inbound_1 > logs/inbound.log
//                                 docker logs ${BUILD_TAG_LOWER}_fakespine_1 > logs/fakespine.log
//                                 docker logs ${BUILD_TAG_LOWER}_rabbitmq_1 > logs/rabbitmq.log
//                                 docker logs ${BUILD_TAG_LOWER}_redis_1 > logs/redis.log
//                                 docker logs ${BUILD_TAG_LOWER}_dynamodb_1 > logs/dynamodb.log
//                             '''
//                             archiveArtifacts artifacts: 'logs/*.log', fingerprint: true
//                             sh label: 'Docker compose logs', script: 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} logs'
//                             sh label: 'Docker compose down', script: 'docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p ${BUILD_TAG_LOWER} down -v'
//                         }
//                     }
//                 }

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
                                            -backend-config="key=${ENVIRONMENT_ID}-mhs.tfstate" \
                                            -backend-config="dynamodb_table=${ENVIRONMENT_ID}-${TF_MHS_LOCK_TABLE_NAME}" \
                                            -input=false -no-color
                                        """
                                    sh label: 'Applying Terraform configuration', script: """
                                            terraform apply -no-color -auto-approve \
                                            -var environment_id=${ENVIRONMENT_ID} \
                                            -var build_id=${BUILD_TAG} \
                                            -var supplier_vpc_id=${SUPPLIER_VPC_ID} \
                                            -var opentest_vpc_id=${OPENTEST_VPC_ID} \
                                            -var dlt_vpc_id=${DLT_VPC_ID} \
                                            -var internal_root_domain=${INTERNAL_ROOT_DOMAIN} \
                                            -var mhs_outbound_service_minimum_instance_count=6 \
                                            -var mhs_outbound_service_maximum_instance_count=9 \
                                            -var mhs_inbound_service_minimum_instance_count=6 \
                                            -var mhs_inbound_service_maximum_instance_count=9 \
                                            -var mhs_route_service_minimum_instance_count=6 \
                                            -var mhs_route_service_maximum_instance_count=9 \
                                            -var task_role_arn=${TASK_ROLE} \
                                            -var execution_role_arn=${TASK_EXECUTION_ROLE} \
                                            -var task_scaling_role_arn=${TASK_SCALING_ROLE} \
                                            -var ecr_address=${DOCKER_REGISTRY} \
                                            -var mhs_outbound_validate_certificate="False" \
                                            -var mhs_log_level=DEBUG \
                                            -var mhs_outbound_http_proxy="" \
                                            -var mhs_state_table_read_capacity=5 \
                                            -var mhs_state_table_write_capacity=10 \
                                            -var mhs_sync_async_table_read_capacity=5 \
                                            -var mhs_sync_async_table_write_capacity=10 \
                                            -var mhs_spine_org_code=${SPINE_ORG_CODE} \
                                            -var inbound_queue_brokers="${MHS_INBOUND_QUEUE_BROKERS}" \
                                            -var inbound_queue_name="${MHS_INBOUND_QUEUE_NAME}" \
                                            -var inbound_queue_username_arn=${INBOUND_QUEUE_USERNAME_ARN} \
                                            -var inbound_queue_password_arn=${INBOUND_QUEUE_PASSWORD_ARN} \
                                            -var inbound_queue_message_ttl=300 \
                                            -var party_key_arn=${PARTY_KEY_ARN} \
                                            -var client_cert_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:build-fakespine-cert-tAch3o \
                                            -var client_key_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:build-fakespine-private-key-6qgFQJ \
                                            -var ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:build-fakespine-ca-store-MZp3Gz \
                                            -var route_ca_certs_arn=arn:aws:secretsmanager:eu-west-2:067756640211:secret:mhs-route.vp-testing.nhsredteam.internal.nhs.uk-zkFNpa \
                                            -var outbound_alb_certificate_arn=arn:aws:acm:eu-west-2:067756640211:certificate/9be6a367-6a0a-4a06-97b1-3ba190eaa2b5 \
                                            -var route_alb_certificate_arn=arn:aws:acm:eu-west-2:067756640211:certificate/5b27c5a6-d8d7-46c6-b7f2-648a27ef806d \
                                            -var mhs_resynchroniser_max_retries=${MHS_RESYNC_RETRIES} \
                                            -var mhs_resynchroniser_interval=${MHS_RESYNC_INTERVAL} \
                                            -var spineroutelookup_service_sds_url=ldap://172.31.18.145 \
                                            -var mhs_ldap_mock_data_url="s3://nhsd-test/mock_ldap_data" \
                                            -var mhs_fake_spine_url=http://172.31.18.145/ \
                                            -var spineroutelookup_service_search_base=${SPINEROUTELOOKUP_SERVICE_SEARCH_BASE} \
                                            -var spineroutelookup_service_disable_sds_tls=${SPINEROUTELOOKUP_SERVICE_DISABLE_TLS} \
                                            -var elasticache_node_type="cache.t2.micro" \
                                            -var mhs_forward_reliable_endpoint_url=http://172.31.18.145:80 \
                                            -var inbound_use_ssl="False" \
                                            -var inbound_server_port="443"
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

                        stage ("Deploy FakeSpine") {
                                                    steps {
                                                        dir ('pipeline/terraform/fakespine-ec2'){
                                                            script {
                                                                String initCommand = """
                                                                    terraform init \
                                                                        -backend-config="bucket=${TF_STATE_BUCKET}" \
                                                                        -backend-config="region=${TF_STATE_BUCKET_REGION}" \
                                                                        -backend-config="key=${ENVIRONMENT_ID}-fakespine.tfstate" \
                                                                        -input=false -no-color
                                                                """
                                                                // Create a consistent list of variables for both Plan and Apply
                                                                Map<String, String> tfVariables = [
                                                                     "environment_id":     "${ENVIRONMENT_ID}",
                                                                     "build_id":           "${BUILD_TAG}",
                                                                     "execution_role_arn": "${TASK_EXECUTION_ROLE}",
                                                                     "ecr_address":        "${DOCKER_REGISTRY}",
                                                                     "mhs_state_bucket":   "${TF_STATE_BUCKET}",
                                                                     "task_role_arn":      "${TASK_ROLE}",
                                                                     "task_scaling_role_arn":          "${TASK_SCALING_ROLE}",
                                                                     "fake_spine_alb_certificate_arn": "${FAKESPINE_ALB_CERT_ARN}", //TODO Check if this can be set with data resource
                                                                     //"inbound_server_base_url":        "${FAKESPINE_INBOUND_URL}", // Inbound is taken from output from MHS
                                                                     "outbound_delay_ms":              "${FAKESPINE_OUTBOUND_DELAY}",
                                                                     "inbound_delay_ms":               "${FAKESPINE_INBOUND_DELAY}",
                                                                     "fake_spine_certificate":         "${FAKESPINE_CERTIFICATE}",
                                                                     "fake_spine_private_key":         "${FAKESPINE_PRIVATE_KEY}",
                                                                     //"fake_spine_ca_store":            "${FAKESPINE_CA_STORE}",
                                                                     "fake_spine_ca_store":            "arn:aws:secretsmanager:eu-west-2:067756640211:secret:vp-testing-fake-spine-ca-store-F42r7k",
                                                                     "party_key_arn":                  "${FAKESPINE_PARTY_KEY}",
                                                                     "fake_spine_outbound_ssl":        "${FAKE_SPINE_OUTBOUND_SSL_ENABLED}",
                                                                     "fake_spine_port":                "${FAKE_SPINE_PORT}",
                                                                     "git_branch_name":                "${GIT_BRANCH}",
                                                                     "git_repo_url":                   "https://github.com/nhsconnect/integration-adaptors",
                                                                     "fake_spine_proxy_validate_cert": "false"
                                                                ]

                                                                sh(label:"Terraform: init", script: initCommand)
                                                                terraform("plan",  "fakespine", ["-no-color"],                  tfVariables )
                                                                terraform("apply", "fakespine", ["-no-color", "-auto-approve"], tfVariables )
                                                                //terraform("destroy", "fakespine", ["-no-color", "-auto-approve"], tfVariables )
                                                            }
                                                        }
                                                    }
                                                }

//                         stage('Integration Tests') {
//                             steps {
//                                 dir('integration-tests/integration_tests') {
//                                     sh label: 'Installing integration test dependencies', script: 'pipenv install --dev --deploy --ignore-pipfile'
//
//                                     // Wait for MHS load balancers to have healthy targets
//                                     dir('../../pipeline/scripts/check-target-group-health') {
//                                         sh script: 'pipenv install'
//
//                                         timeout(13) {
//                                             waitUntil {
//                                                 script {
//                                                     def r = sh script: 'sleep 10; AWS_DEFAULT_REGION=eu-west-2 pipenv run main ${MHS_OUTBOUND_TARGET_GROUP} ${MHS_INBOUND_TARGET_GROUP}  ${MHS_ROUTE_TARGET_GROUP}', returnStatus: true
//                                                     return (r == 0);
//                                                 }
//                                             }
//                                         }
//                                     }
//                                     sh label: 'Running integration tests', script: 'pipenv run inttests'
//                                 }
//                             }
//                         }
                    }
                }
//             } // parallel
//         }
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

void terraform(String action, String component, List<String> parameters, Map<String, String> variables, Map<String, String> backendConfig=[:]) {
    List<String> variablesList=variables.collect { key, value -> "-var ${key}=${value}" }
    String command = "terraform ${action} ${parameters.join(" ")} ${variablesList.join(" ")}"
    sh(label:"Terraform: "+action, script: command)
}
