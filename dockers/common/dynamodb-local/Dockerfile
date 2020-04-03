FROM amazon/dynamodb-local

USER root

RUN yum install --assumeyes --quiet python3 && pip3 install -q awscli

USER dynamodblocal

# Create a table called mhs_state with primary key "key"
RUN nohup bash -c "java -jar DynamoDBLocal.jar -sharedDb &" && \
        AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws dynamodb \
        --endpoint-url http://localhost:8000 \
        --region eu-west-2 create-table \
        --table-name mhs_state \
        --attribute-definitions AttributeName=key,AttributeType=S \
        --key-schema AttributeName=key,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 && \
         AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws dynamodb \
        --endpoint-url http://localhost:8000 \
        --region eu-west-2 create-table \
        --table-name sync_async_state \
        --attribute-definitions AttributeName=key,AttributeType=S \
        --key-schema AttributeName=key,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

# I tried using CMD/ENTRYPOINT to run DynamoDB but kept getting errors, so
# switched to this approach instead.
RUN printf "#!/bin/sh\njava -jar DynamoDBLocal.jar -sharedDb\n" > run-db.sh
RUN chmod +x run-db.sh

ENTRYPOINT ["/home/dynamodblocal/run-db.sh"]
