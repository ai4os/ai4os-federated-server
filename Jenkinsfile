@Library(['github.com/indigo-dc/jenkins-pipeline-library@release/2.1.1']) _

def projectConfig

pipeline {
    agent any

    stages {
        stage("Variable initialization") {
            steps {
                checkout scm
                script {
                    withFolderProperties{
                        docker_registry = env.AI4OS_REGISTRY
                        docker_registry_credentials = env.AI4OS_REGISTRY_CREDENTIALS
                        docker_registry_org = env.AI4OS_REGISTRY_REPOSITORY
                    }
                    // get docker image name from metadata.json
                    meta = readJSON file: "metadata.json"
                    image_name = meta["sources"]["docker_registry_repo"].split("/")[1]
                    app_docker_tag = "${env.BRANCH_NAME == 'main' ? 'latest' : env.BRANCH_NAME}" 
                    APP_DOCKER_IMAGE = docker_registry_org + "/" + image_name + ":" + app_docker_tag
                }
            }
        }
        stage('Application testing') {
            steps {
                script {
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
            publishHTML([allowMissing: false, 
                                 alwaysLinkToLastBuild: false, 
                                 keepAll: true, 
                                 reportDir: "htmlcov", 
                                 reportFiles: 'index.html', 
                                 reportName: 'Coverage report', 
                                 reportTitles: ''])
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

