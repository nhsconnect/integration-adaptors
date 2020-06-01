String region = "eu-west-2"

pipeline {
  agent{
    label 'jenkins-workers'
  } //agent

  options {
    buildDiscarder(logRotator(numToKeepStr: '15'))
  }

  parameters {
    choice (name: "Project",     choices: ['nia'],                                                description: "Choose a project")
    choice (name: "Environment", choices: ['build1', 'build2', 'build3', 'vp', 'ptl', 'account'], description: "Choose environment")
    choice (name: "Component",   choices: ['base', 'nhais', 'account'],                           description: "Choose component")
    choice (name: "Action",      choices: ['plan', 'apply', 'plan-destroy', 'destroy'],           description: "Choose Terraform action")
    string (name: "Variables",   defaultValue: "",                                                description: "Terrafrom variables, format: variable1=value,variable2=value, no spaces")
    string (name: "Git_Branch",  defaultValue: "develop",                    description: "Git branch")
    string (name: "Git_Repo",    defaultValue: "https://github.com/nhsconnect/integration-adaptor-nhais.git", description: "Git Repo to clone")
  }

  stages {
    stage("Clone the repository") {
      steps {
        git (branch: params.Git_Branch, url: params.Git_Repo)
        script {
          //println(sh(label: "Check the directory contents", script: "ls -laR", returnStdout: true))
          //String buildUser = ""
          // wrap([$class: 'BuildUser']) { buildUser = env.BUILD_USER } //TODO install build user vars plugin
          currentBuild.description = "TF: ${params.Action} | env: ${params.Environment} | cmp: ${params.Component}"
          //println("TODO Clone the branch from Git_Branch")
        } // script
      }  // steps
    } // stage Clone

    stage("Terraform Plan") {
      steps {
        dir("terraform/aws") {
          script {
            // prepare variables map
            Map<String, String> variablesMap = [:]
            List<String> variablesList = params.Variables.split(",")
            variablesList.each {
              def kvp = it.split("=")
              if (kvp.length > 1) {
                variablesMap.put(kvp[0],kvp[1])
              }
            }
               
            List<String> tfParams = []
            if (params.Action == "destroy" || params.Action == "plan-destroy") {tfParams.add("-destroy")}
            if (terraformInit(TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region) !=0) { error("Terraform init failed")}
            if (terraform('plan', TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region, variablesMap, tfParams) !=0 ) { error("Terraform Plan failed")}
          } // script
        } //dir terraform/aws
      } // steps
    } // stage Terraform Plan

    stage("Terraform Apply") {
      when {
        expression {
          params.Action == "apply" || params.Action == "destroy"
        }
      }
      steps {
        dir("terraform/aws") {
          script {
            if (terraform(params.Action, TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region, variablesMap) !=0 ) { error("Terraform Plan failed")}
          } // script
        } //dir terraform/aws
      } // steps
    } // stage Terraform Apply
  } // stages
} // pipeline

int terraformInit(String tfStateBucket, String project, String environment, String component, String region) {
  println("Terraform Init for Environment: ${environment} Component: ${Component} in region: ${region} using bucket: ${tfStateBucket}")
  String command = "terraform init -backend-config='bucket=${tfStateBucket}' -backend-config='region=${region}' -backend-config='key=${project}-${environment}-${component}.tfstate' -input=false -no-color"
  dir("components/${component}") {
    return( sh( label: "Terraform Init", script: command, returnStatus: true))
  } // dir
} // int TerraformInit

int terraform(String action, String tfStateBucket, String project, String environment, String component, String region, Map<String, String> variables=[:], List<String> parameters=[]) {
    println("Running Terraform ${action} in region ${region} with: \n Project: ${project} \n Environment: ${environment} \n Component: ${component}")
    variablesMap = variables
    variablesMap.put('region',region)
    variablesMap.put('project', project)
    variablesMap.put('environment', environment)
    variablesMap.put('tf_state_bucket',tfStateBucket)
    parametersList = parameters
    parametersList.add("-no-color")
    //parametersList.add("-compact-warnings")  /TODO update terraform to have this working
    List<String> variableFilesList = [
      "-var-file=../../etc/global.tfvars",
      "-var-file=../../etc/${region}_${environment}.tfvars"
    ]
    if (action == "apply"|| action == "destroy") {parametersList.add("-auto-approve")}
    List<String> variablesList=variablesMap.collect { key, value -> "-var ${key}=${value}" }
    String command = "terraform ${action} ${variableFilesList.join(" ")} ${parametersList.join(" ")} ${variablesList.join(" ")} "
    dir("components/${component}") {
      return sh(label:"Terraform: "+action, script: command, returnStatus: true)
    } // dir
} // int Terraform
