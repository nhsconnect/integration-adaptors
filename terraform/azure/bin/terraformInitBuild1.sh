export TF_PROJECT="nia"
export TF_ENVIRONMENT="build1"
export TF_COMPONENT=$(basename $(pwd))
export TF_STATE_CONTAINER=${TF_PROJECT}-state-container
export TF_STATE_ACCOUNT=${TF_PROJECT}state

terraform init -backend-config=key=${TF_PROJECT}-${TF_ENVIRONMENT}-${TF_COMPONENT} -backend-config=container_name=${TF_STATE_CONTAINER} -backend-config=storage_account_name=${TF_STATE_ACCOUNT}
