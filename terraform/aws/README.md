# Deployment of adaptors on Amazon Web Services

## Terraform

## Known Limitations

## Terraform structure and details

### 2. [components](components) - directory for components, each adaptor is a separate component and is deployed separately

#### 2.1 [components/account](components/account) - directory for resources existing once per account and shared by all environments and components

#### 2.2 [components/base](components/base) - directory for resources existing once per environment and shared by all components

#### 2.3 [components/mhs](components/mhs) - directory for resources used by MHS component

#### 2.4 [components/nhais](components/nhais) - directory for resources used by NHAIS component

### 3. [etc](etc) - directory for setting in tfvars

### 4. [modules](modules) - directory for Terraform modules - groups of resources that can be used a single resources in components

## Deploying

## HSCN VPC Config
