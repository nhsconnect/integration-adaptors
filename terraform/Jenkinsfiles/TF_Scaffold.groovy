String region = "eu-west-2"

Map <String, Map<String, String>> componentImageBranch = [
  OneOneOne:       [ecrRepo: "111",                  branch: "master"],
  nhais:           [ecrRepo: "nhais",                branch: "develop"],
  nhais_responder: [ecrRepo: "nhais-fake-responder", branch: "origin-develop"],
  gp2gp:           [ecrRepo: "gp2gp",                branch: "main"],
  mhs:             [ecrRepo: "mhs/outbound",         branch: "develop"], // mhs/route and mhs/inboud will have the same tag, no need to search in them
  "lab-results":     [ecrRepo: "lab-results",          branch: "main"],
  pss:           [ecrRepo: "pss",                    branch: "main"]
]

pipeline {
  agent{
    label 'jenkins-workers'
  } //agent

  options {
    buildDiscarder(logRotator(numToKeepStr: '15'))
  }

  parameters {
    choice (name: "Project",     choices: ['nia'],                                                description: "Choose a project")
    choice (name: "Environment", choices: ['ptl', 'account'],                                     description: "Choose environment")
    choice (name: "Component",   choices: ['base', 'nhais', 'OneOneOne', 'mhs', 'account', 'fake_mesh', 'nhais_responder', 'gp2gp', 'lab-results', 'pss'],     description: "Choose component")
    choice (name: "Action",      choices: ['plan', 'apply', 'plan-destroy', 'destroy'],           description: "Choose Terraform action")
    string (name: "Variables",   defaultValue: "",                                                description: "Terrafrom variables, format: variable1=value,variable2=value, no spaces")
    string (name: "Targets",     defaultValue: "",                                                description: "Resources to be targeted by plan/apply/destroy, format: [resource type1].[resource_name1],[resource type2].[resource name2], no spaces")
    string (name: "Git_Branch",  defaultValue: "develop",                                         description: "Git branch from which TF will be taken")
    string (name: "Git_Repo",    defaultValue: "https://github.com/nhsconnect/integration-adaptors.git", description: "Git Repo with TF Code")
  }

  stages {
    stage("Clone the repository") {
      steps {
        dir ("integration-adaptors") {
          git (branch: params.Git_Branch, url: params.Git_Repo)
          script {
          //println(sh(label: "Check the directory contents", script: "ls -laR", returnStdout: true))
          //String buildUser = ""
          // wrap([$class: 'BuildUser']) { buildUser = env.BUILD_USER } //TODO install build user vars plugin
          currentBuild.description = "TF: ${params.Action} | env: ${params.Environment} | cmp: ${params.Component}"
          //println("TODO Clone the branch from Git_Branch")
          } // script
        } // dir integration-adaptors
      }  // steps
    } // stage Clone

    stage("Terraform Plan") {
      options {
        lock("${params.Project}-${params.Environment}-${params.Component}")
      }
      steps {
        dir("integration-adaptors/terraform/aws") {
          script {
            // prepare variables map
            Map<String, String> variablesMap = [:]

            //Get the build_id variable if in application component
            if (componentImageBranch.containsKey(params.Component)) {
              variablesMap.put("${params.Component}_build_id", getLatestImageTag(componentImageBranch[params.Component].branch, componentImageBranch[params.Component].ecrRepo, region))
            }

            // Get the variables from job parameters
            List<String> variablesList = params.Variables.split(",")
            variablesList.each {
              def kvp = it.split("=")
              if (kvp.length > 1) {
                variablesMap.put(kvp[0],kvp[1])
              }
            }
            List<String> tfParams = []
            List<String> targetsList = params.Targets.split(",")
            List<String> tfTargets = []
            targetsList.each {
              if (it != "") {
                tfTargets.add("-target=${it}")
              }
            }

            if (params.Action == "destroy" || params.Action == "plan-destroy") {tfParams.add("-destroy")}
            if (terraformInit(TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region) !=0) { error("Terraform init failed")}
            if (terraform('plan', TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region, variablesMap, tfParams.plus(tfTargets)) !=0 ) { error("Terraform Plan failed")}
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
      options {
        lock("${params.Project}-${params.Environment}-${params.Component}")
      }
      steps {
        dir("integration-adaptors/terraform/aws") {
          script {
            Map<String, String> variablesMap = [:]

            //Get the build_id variable if in application component
            if (componentImageBranch.containsKey(params.Component)) {
              variablesMap.put("${params.Component}_build_id", getLatestImageTag(componentImageBranch[params.Component].branch, componentImageBranch[params.Component].ecrRepo, region))
            }

            // Get the variables from job parameters
            List<String> variablesList = params.Variables.split(",")
            variablesList.each {
              def kvp = it.split("=")
              if (kvp.length > 1) {
                variablesMap.put(kvp[0],kvp[1])
              }
            }
            List<String> tfParams = []
            List<String> targetsList = params.Targets.split(",")
            List<String> tfTargets = []
            targetsList.each {
              if (it != "") {
                tfTargets.add("-target=${it}")
              }
            }

            if (terraform(params.Action, TF_STATE_BUCKET, params.Project, params.Environment, params.Component, region, variablesMap, tfTargets) !=0 ) { error("Terraform Apply failed")}
          } // script
        } //dir terraform/aws
      } // steps
    } // stage Terraform Apply
  } // stages
} // pipeline
String tfEnv(String tfEnvRepo="https://github.com/tfutils/tfenv.git", String tfEnvPath="~/.tfenv") {
  sh(label: "Get tfenv" ,  script: "git clone ${tfEnvRepo} ${tfEnvPath}", returnStatus: true)
  sh(label: "Install TF",  script: "${tfEnvPath}/bin/tfenv install"     , returnStatus: true)
  return "${tfEnvPath}/bin/terraform"
}

int terraformInit(String tfStateBucket, String project, String environment, String component, String region) {
  String terraformBinPath = tfEnv()
  println("Terraform Init for Environment: ${environment} Component: ${component} in region: ${region} using bucket: ${tfStateBucket}")
  String command = "${terraformBinPath} init -backend-config='bucket=${tfStateBucket}' -backend-config='region=${region}' -backend-config='key=${project}-${environment}-${component}.tfstate' -input=false -no-color"
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

    // Get the secret variables for global
    String secretsFile = "etc/secrets.tfvars"
    writeVariablesToFile(secretsFile,getAllSecretsForEnvironment(environment,"nia",region))
    String terraformBinPath = tfEnv()

    List<String> variableFilesList = [
      "-var-file=../../etc/global.tfvars",
      "-var-file=../../etc/${region}_${environment}.tfvars",
      "-var-file=../../${secretsFile}"
    ]
    if (action == "apply"|| action == "destroy") {parametersList.add("-auto-approve")}
    List<String> variablesList=variablesMap.collect { key, value -> "-var ${key}=${value}" }
    String command = "${terraformBinPath} ${action} ${variableFilesList.join(" ")} ${parametersList.join(" ")} ${variablesList.join(" ")} "
    dir("components/${component}") {
      return sh(label:"Terraform: "+action, script: command, returnStatus: true)
    } // dir
} // int Terraform

Map<String,String> collectTfOutputs(String component) {
  Map<String,String> returnMap = [:]
  dir("components/${component}") {
    String terraformBinPath = tfEnv()
    List<String> outputsList = sh (label: "Listing TF outputs", script: "${terraformBinPath} output", returnStdout: true).split("\n")
    outputsList.each {
      returnMap.put(it.split("=")[0].trim(),it.split("=")[1].trim())
    }
  } // dir
  return returnMap
}

// Retrieving Secrets from AWS Secrets
String getSecretValue(String secretName, String region) {
  String awsCommand = "aws secretsmanager get-secret-value --region ${region} --secret-id ${secretName} --query SecretString --output text"
  return sh(script: awsCommand, returnStdout: true).trim()
}

Map<String,Object> decodeSecretKeyValue(String rawSecret) {
  List<String> secretsSplitted = rawSecret.replace("{","").replace("}","").split(",")
  Map<String,Object> secretsDecoded = [:]
  secretsSplitted.each {
    String key = it.split(":")[0].trim().replace("\"","")
    Object value = it.split(":")[1]
    secretsDecoded.put(key,value)
  }
  return secretsDecoded
}

List<String> getSecretsByPrefix(String prefix, String region) {
  String awsCommand = "aws secretsmanager list-secrets --region ${region} --query SecretList[].Name --output text"
  List<String> awsReturnValue = sh(script: awsCommand, returnStdout: true).split()
  return awsReturnValue.findAll { it.startsWith(prefix) }
}

Map<String,Object> getAllSecretsForEnvironment(String environment, String secretsPrefix, String region) {
  List<String> globalSecrets = getSecretsByPrefix("${secretsPrefix}-global",region)
  println "global secrets:" + globalSecrets
  List<String> environmentSecrets = getSecretsByPrefix("${secretsPrefix}-${environment}",region)
  println "env secrets:" + environmentSecrets
  Map<String,Object> secretsMerged = [:]
  globalSecrets.each {
    String rawSecret = getSecretValue(it,region)
    if (it.contains("-kvp")) {
      secretsMerged << decodeSecretKeyValue(rawSecret)
    } else {
      secretsMerged.put(it.replace("${secretsPrefix}-global-",""),rawSecret)
    }
  }
  environmentSecrets.each {
    String rawSecret = getSecretValue(it,region)
    if (it.contains("-kvp")) {
      secretsMerged << decodeSecretKeyValue(rawSecret)
    } else {
      secretsMerged.put(it.replace("${secretsPrefix}-${environment}-",""),rawSecret)
    }
  }
  return secretsMerged
}

void writeVariablesToFile(String fileName, Map<String,Object> variablesMap) {
  List<String> variablesList=variablesMap.collect { key, value -> "${key} = ${value}" }
  sh (script: "touch ${fileName} && echo '\n' > ${fileName}")
  variablesList.each {
    sh (script: "echo '${it}' >> ${fileName}")
  }
}

// Retrieving Docker images from ECR

List<String> getAllImageTagsByPrefix(String prefix, String ecrRepo, String region) {
  String awsCommand = "aws ecr list-images --repository-name ${ecrRepo} --region ${region} --query imageIds[].imageTag --output text"
  List<String> allImageTags = sh (script: awsCommand, returnStdout: true).split()
  return allImageTags.findAll{it.startsWith(prefix)}
}

String getLatestImageTag(String prefix, String ecrRepo, String region) {
  List<String> imageTags = getAllImageTagsByPrefix(prefix, ecrRepo, region)
  Map<Integer, String> buildNumberTag = [:]
  Integer maxBuild = 0
  imageTags.each {
    Integer currBuild = it.replace("${prefix}-","").split("-")[0]
    buildNumberTag.put(currBuild, it)
    if (currBuild  > maxBuild) { maxBuild = currBuild}
  }
  return buildNumberTag[maxBuild]
}
