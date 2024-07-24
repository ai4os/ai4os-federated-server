@Library(['github.com/indigo-dc/jenkins-pipeline-library@release/2.1.1']) _

def projectConfig

pipeline {
    agent any

    environment {
        //JPL_DOCKERSERVER = "https://registry.services.ai4os.euu/"
        //JPL_DOCKERUSER = "ai4os-hub"
        //JPL_DOCKERPASS = credentials('AIOS-registry-credentials')
        APP_DOCKER_IMAGE = "ai4os-federated-server"
        APP_DOCKER_TAG = "${env.BRANCH_NAME == 'main' ? 'latest' : env.BRANCH_NAME}" 
    }

    stages {
        stage("Variable initialization") {
            steps {
                script {
                    withFolderProperties{
                        env.JPL_DOCKERSERVER = env.AI4OS_REGISTRY
                        env.JPL_DOCKERUSER = env.AI4OS_REGISTRY_REPOSITORY
                        env.JPL_DOCKERPASS = env.AI4OS_REGISTRY_CREDENTIALS
                    }
                    println ("[DEBUG1] Docker image to push: $APP_DOCKER_IMAGE, $env.APP_DOCKER_IMAGE, via $JPL_DOCKERUSER to $JPL_DOCKERSERVER (${env.JPL_DOCKERSERVER})")
                }
            }
        }
        stage('Application testing') {
            steps {
                script {
                    println ("[DEBUG2] Docker image to push: $APP_DOCKER_IMAGE, $env.APP_DOCKER_IMAGE, via $JPL_DOCKERUSER to $JPL_DOCKERSERVER (${env.JPL_DOCKERSERVER})")
                    projectConfig = pipelineConfig()
                    buildStages(projectConfig)
                }
            }
        }
    }
    post {
        // publish results and clean-up
        always {
            // file locations are defined in tox.ini
            // publish results of the style analysis
            recordIssues(enabledForFailure: true,
                         tools: [flake8(pattern: 'flake8.log',
                                 name: 'PEP8 report',
                                 id: "flake8_pylint")])
            // publish results of the coverage test
            //publishHTML([allowMissing: false, 
            //                     alwaysLinkToLastBuild: false, 
            //                     keepAll: true, 
            //                     reportDir: "htmlcov", 
            //                     reportFiles: 'index.html', 
            //                     reportName: 'Coverage report', 
            //                     reportTitles: ''])
            // publish results of the security check
            publishHTML([allowMissing: false, 
                         alwaysLinkToLastBuild: false, 
                         keepAll: true, 
                         reportDir: "bandit", 
                         reportFiles: 'index.html', 
                         reportName: 'Bandit report', 
                         reportTitles: ''])
            // Clean after build
            cleanWs()
        }    
    }
}

