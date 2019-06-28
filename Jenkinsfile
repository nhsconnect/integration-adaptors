pipeline {
    agent any

    environment {
      BUILD_TAG = sh label: 'Generating build tag', returnStdout: true, script: 'python build/scripts/tag.py ${GIT_BRANCH} ${BUILD_NUMBER}'
    }

    stages {
        stage('Unit Tests') {
            steps {
                dir('mhs-reference-implementation') {
                    sh label: 'Installing dependencies', script: 'pipenv install --deploy --ignore-pipfile'
                    sh label: 'Running unit tests', script: 'pipenv run tests'
                }
            }
        }

        stage('Package') {
            steps {
                sh label: 'Running Packer build', script: 'packer build build/packer/mhs.json'
            }
        }
    }
}
