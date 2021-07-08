pipeline {
    agent any

    triggers {
        pollSCM('*/5 * * * 1-5')
    }

    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
      PATH="/var/lib/jenkins/miniconda3/bin:$PATH"
    }

    stages {

        stage ("Code pull"){
            steps{
                checkout scm
            }
        }

        stage('Build environment') {
            steps {
                echo "Building virtualenv"
                sh  ''' conda create --yes -n ${BUILD_TAG} python
                        source activate ${BUILD_TAG}
                        pip install -r requirements/dev.txt
                    '''
            }
        }

        stage('Static code metrics') {
            steps {
                echo "Raw metrics"
                sh  ''' source activate ${BUILD_TAG}
                        radon raw --json pandasdatacube > raw_report.json
                        radon cc --json pandasdatacube > cc_report.json
                        radon mi --json pandasdatacube > mi_report.json
                        sloccount --duplicates --wide pandasdatacube > sloccount.sc
                    '''
                echo "Test coverage"
                sh  ''' source activate ${BUILD_TAG}
                        coverage run unittest discover
                        python -m coverage xml -o reports/coverage.xml
                    '''
                echo "Style check"
                sh  ''' source activate ${BUILD_TAG}
                        pylint pandasdatacube || true
                    '''
            }
            post{
                always{
                    step([$class: 'CoberturaPublisher',
                                   autoUpdateHealth: false,
                                   autoUpdateStability: false,
                                   coberturaReportFile: 'reports/coverage.xml',
                                   failNoReports: false,
                                   failUnhealthy: false,
                                   failUnstable: false,
                                   maxNumberOfBuilds: 10,
                                   onlyStable: false,
                                   sourceEncoding: 'ASCII',
                                   zoomCoverageChart: false])
                }
            }
        }

        stage('Unit tests') {
            steps {
                sh  ''' source activate ${BUILD_TAG}
                        python -m pytest --verbose --junit-xml reports/unit_tests.xml
                    '''
            }
            post {
                always {
                    // Archive unit tests for the future
                    junit (allowEmptyResults: true,
                          testResults: './reports/unit_tests.xml')
                }
            }
        }

        stage('Integration tests') {
            steps {
                sh  ''' source activate ${BUILD_TAG}
                        behave -f=formatters.cucumber_json:PrettyCucumberJSONFormatter -o ./reports/integration.json
                    '''
            }
            post {
                always {
                    cucumber (fileIncludePattern: '**/*.json',
                              jsonReportDirectory: './reports/',
                              parallelTesting: true,
                              sortingMethod: 'ALPHABETICAL')
                }
            }
        }

        stage('Build package') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh  ''' source activate ${BUILD_TAG}
                        python setup.py bdist_wheel
                    '''
            }
            post {
                always {
                    // Archive unit tests for the future
                    archiveArtifacts (allowEmptyArchive: true,
                                     artifacts: 'dist/*whl',
                                     fingerprint: true)
                }
            }
        }

        stage("Deploy to PyPI") {
            steps {
                sh "twine upload dist/*"
            }
        }
    }

    post {
        always {
            sh 'conda remove --yes -n ${BUILD_TAG} --all'
        }
        failure {
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}