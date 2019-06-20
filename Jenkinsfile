pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                dir('mhs-reference-implementation') {
                    sh label: 'Installing dependencies', script: 'pipenv install --deploy --ignore-pipfile'
                    sh label: 'Running unit tests', script: 'pipenv run tests'
                }
            }
        }
    }
}
