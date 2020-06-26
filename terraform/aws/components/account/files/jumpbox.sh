#!/bin/bash

# export aws="$(which aws || echo '/usr/bin/aws')";
# export curl="$(which curl || echo '/usr/bin/curl')";

echo "Update the system"
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum makecache
yum update -y

echo "Install software"
yum install -y docker git mongodb python3
pip3 install awscli

echo "Setup MOTD"
echo "  " >> /etc/motd
echo "Welcome to NIA Jumpbox" >> /etc/motd
echo "  " >> /etc/motd
echo "Useful commands:" >> /etc/motd
echo "List all DocDB clusters endpoints in the account: \t aws docdb describe-db-clusters --region eu-west-2 --query 'DBClusters[].Endpoint'" >> /etc/motd
echo "Get the username for DocDB: aws secretsmanager \t get-secret-value --region eu-west-2 --secret-id docdb-master-username --query 'SecretString'" >> /etc/motd
echo "Get the password for DocDB: aws secretsmanager \t get-secret-value --region eu-west-2 --secret-id docdb-master-password --query 'SecretString'" >> /etc/motd
echo "List LoadBalancer endpoints for applications: \t aws elbv2 describe-load-balancers --region eu-west-2 --query 'LoadBalancers[].DNSName' | grep nia" >> /etc/motd
