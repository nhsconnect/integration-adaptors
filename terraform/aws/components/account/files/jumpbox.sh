#!/bin/bash

export aws="$(which aws || echo '/usr/bin/aws')";
export curl="$(which curl || echo '/usr/bin/curl')";

echo "Update the system"
yum makecache
yum update


echo "Install software"
yum install -y docker git
