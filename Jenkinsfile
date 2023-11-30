#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library@1.4.0']) _

def job_result_url = ''

pipeline {
    agent {
        docker { image 'indigodatacloud/ci-images:python3.10' }
    }

    environment {         
        author_name = "Judith Sáinz-Pardo"         
        author_email = "sainzpardo@ifca.unican.es"         
        app_name = "fedserver"         
        job_location = "Pipeline-as-code/DEEP-OC-org/DEEP-OC-federated-server/${env.BRANCH_NAME}"     
    }

    stages {
        stage('Code fetching') {
            steps {
                checkout scm
            }
        }

        stage('Style analysis: PEP8') {
            steps {
                ToxEnvRun('pep8')
            }
            post {
                always {
                    recordIssues(tools: [flake8(pattern: 'flake8.log')])
                }
            }
        }

        stage('Unit testing coverage') {
            steps {
                ToxEnvRun('cover')
                ToxEnvRun('cobertura')
            }
            //post {
            //   success {
            //        HTMLReport('cover', 'index.html', 'coverage.py report')
            //        CoberturaReport('**/coverage.xml')
            //    }
            //}
        }

        //stage('Metrics gathering') {
        //   agent {
        //        label 'sloc'
        //    }
        //    steps {
        //        checkout scm
        //        SLOCRun()
        //    }
        //    post {
        //        success {
        //            SLOCPublish()
        //        }
        //    }
        //}

        stage('Security scanner') {
            steps {
                ToxEnvRun('bandit-report')
                script {
                    if (currentBuild.result == 'FAILURE') {
                        currentBuild.result = 'UNSTABLE'
                    }
               }
            }
            post {
               always {
                    HTMLReport("/tmp/bandit", 'index.html', 'Bandit report')
                }
            }
        }

        stage("Re-build Docker images") {
            when {
                anyOf {
                   branch 'main'
                   branch 'test'
                   buildingTag()
               }
            }
            steps {
                script {
                    def job_result = JenkinsBuildJob("${env.job_location}")
                    job_result_url = job_result.absoluteUrl
                }
            }
        }

}
}
