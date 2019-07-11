pipeline {
    agent any

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python3 pipeline/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
    }

    stages {
        stage('Unit Tests') {
            steps {
                dir('mhs-reference-implementation') {
                    sh label: 'Installing dependencies', script: 'pipenv install --deploy --ignore-pipfile'
                    sh label: 'Running unit tests', script: 'pipenv run unittests'
                    sh label: 'Running unit tests', script: 'pipenv run inttests'
               }
            }
        }

        stage('Package') {
            steps {
                sh label: 'Running Packer build', script: 'packer build pipeline/packer/mhs.json'
            }
        }
    }
}
