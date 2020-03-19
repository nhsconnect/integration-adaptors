#!/bin/bash

export MHS_LOG_LEVEL=INFO
export MHS_SECRET_PARTY_KEY=fake
export MHS_SECRET_CLIENT_CERT=""
export MHS_SECRET_CLIENT_KEY=""
export MHS_SECRET_CA_CERTS=""
export MHS_INBOUND_QUEUE_URL=amqp://localhost:5672/inbound
export MHS_INBOUND_RAW_QUEUE_URL=amqp://localhost:5672/raw-inbound
export MHS_SECRET_INBOUND_QUEUE_USERNAME=guest
export MHS_SECRET_INBOUND_QUEUE_PASSWORD=guest
export MHS_STATE_TABLE_NAME=mhs_state
export MHS_SYNC_ASYNC_STATE_TABLE_NAME=sync_async_state
export MHS_DYNAMODB_ENDPOINT_URL=http://localhost:8000
# boto3 requires some AWS creds to be provided, even
# when connecting to local DynamoDB
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export MHS_NO_TLS=True
