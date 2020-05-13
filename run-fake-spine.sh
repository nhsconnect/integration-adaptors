source ./fake-spine-env.sh
BUILD_TAG=latest
docker build -t local/fake-spine:${BUILD_TAG} -f ./integration-tests/fake_spine/Dockerfile .
docker run -e FAKE_SPINE_PORT -e INBOUND_PROXY_PORT -e INBOUND_SERVER_BASE_URL -e OUTBOUND_DELAY_MS -e INBOUND_DELAY_MS \
 -e FAKE_SPINE_OUTBOUND_SSL_ENABLED  -e FAKE_SPINE_CERTIFICATE -e MHS_SECRET_PARTY_KEY -e FAKE_SPINE_PRIVATE_KEY \
 -e FAKE_SPINE_CA_STORE -e FAKE_SPINE_PROXY_VALIDATE_CERT -e MHS_LOG_LEVEL \
 --log-driver=awslogs --log-opt awslogs-region=eu-west-2 --log-opt awslogs-group=/aws/ec2/fake-spine-ec2-instance --log-opt awslogs-create-group=true \
 -d -p 80:80 -p 443:443 "local/fake-spine:${BUILD_TAG}"
