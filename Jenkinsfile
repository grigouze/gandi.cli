pipeline {
  agent any
  stages {
    stage('stage') {
      steps {
        sh 'echo "bla"'
      }
    }
    stage('hhh') {
      steps {
        sh 'python setup.py tests'
      }
    }
  }
}