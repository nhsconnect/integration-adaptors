pipeline {
    agent { docker { image 'python:3' } }
    stages {
        stage('build') {
            steps {
                dir('mhs-reference-implementation') {
                    sh 'python --version'
                }
            }
        }
    }
}
