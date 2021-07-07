pipeline {
  agent any
  stages {
    stage('Code pull') {
      steps {
        checkout scm
      }
    }

    stage('Build environment') {
      steps {
        sh '''conda create --yes -n ${BUILD_TAG} python
                      source activate ${BUILD_TAG}
                      pip install -r requirements.txt
                    '''
      }
    }

    stage('Test environment') {
      steps {
        sh '''source activate ${BUILD_TAG}
                      pip list
                      which pip
                      which python
                    '''
      }
    }

  }
  environment {
    PATH = "/var/lib/jenkins/miniconda3/bin:$PATH"
  }
  post {
    always {
      sh 'conda remove --yes -n ${BUILD_TAG} --all'
    }

    failure {
      echo 'Send e-mail, when failed'
    }

  }
  options {
    skipDefaultCheckout(true)
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timestamps()
  }
  triggers {
    pollSCM('*/5 * * * 1-5')
  }
}