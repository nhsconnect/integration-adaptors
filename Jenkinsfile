pipeline {
    agent {
        docker { image 'mc706/pipenv-3.7' }
    }
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
