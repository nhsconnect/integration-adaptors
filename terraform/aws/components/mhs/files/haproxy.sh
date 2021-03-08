#!/bin/bash

# export aws="$(which aws || echo '/usr/bin/aws')";
# export curl="$(which curl || echo '/usr/bin/curl')";

echo "Update the system"
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum makecache
yum update -y

echo "Install software"
yum install -y docker git mongodb python3 haproxy
amazon-linux-extras install -y java-openjdk11
pip3 install awscli