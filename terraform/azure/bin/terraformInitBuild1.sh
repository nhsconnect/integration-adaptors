export TF_PROJECT="nia"
export TF_ENVIRONMENT="build1"
export TF_COMPONENT=$(basename $(pwd))
export TF_STATE_CONTAINER=${TF_PROJECT}-state-container
export TF_STATE_ACCOUNT=${TF_PROJECT}state
export TF_STATE_RESOURCE_GROUP=${TF_PROJECT}-state-rg

echo $TF_PROJECT
echo "TF_PROJECT = ${TF_PROJECT}"
echo "TF_ENVIRONMENT = ${TF_ENVIRONMENT}"
echo "TF_COMPONENT = ${TF_COMPONENT}"
echo "TF_STATE_CONTAINER = ${TF_STATE_CONTAINER}"
echo "TF_STATE_ACCOUNT = ${TF_STATE_ACCOUNT}"
echo "TF_STATE_RESOURCE_GROUP = ${TF_STATE_RESOURCE_GROUP}"


terraform init -backend-config=resource_group_name=${TF_STATE_RESOURCE_GROUP} -backend-config=key=${TF_PROJECT}-${TF_ENVIRONMENT}-${TF_COMPONENT} -backend-config=container_name=${TF_STATE_CONTAINER} -backend-config=storage_account_name=${TF_STATE_ACCOUNT}

