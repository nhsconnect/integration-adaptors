pipeline {
    agent any
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
                sh label: 'Running Packer build', script: 'packer build packer\mhs.json'
            }
        }
    }
}
