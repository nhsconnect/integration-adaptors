#!/bin/bash

# export aws="$(which aws || echo '/usr/bin/aws')";
# export curl="$(which curl || echo '/usr/bin/curl')";

echo "Update the system"
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum makecache
yum update -y

echo "Install software"
yum install -y docker git mongodb python3
amazon-linux-extras install -y java-openjdk11
pip3 install awscli

export MOTDFILE = /etc/update-motd.d/80-nia
echo "Setup MOTD"
echo "echo  ' '" >> $MOTDFILE
echo "echo 'Welcome to NIA Jumpbox'" >> $MOTDFILE
echo "echo  ' '" >> $MOTDFILE
echo "echo  'Useful commands:'" >> $MOTDFILE
echo "echo  'List all DocDB clusters endpoints in the account:  aws docdb describe-db-clusters --region eu-west-2 --query \'DBClusters[].Endpoint\''" >> $MOTDFILE
echo "echo  'Get the username for DocDB: aws secretsmanager get-secret-value --region eu-west-2 --secret-id docdb-master-username --query \'SecretString\''" >> $MOTDFILE
echo "echo  'Get the password for DocDB: aws secretsmanager get-secret-value --region eu-west-2 --secret-id docdb-master-password --query \'SecretString\''" >> $MOTDFILE
echo "echo  'List LoadBalancer endpoints for applications: aws elbv2 describe-load-balancers --region eu-west-2 --query \'LoadBalancers[].DNSName\' | grep nia'" >> $MOTDFILE
