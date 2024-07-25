@Library(['github.com/indigo-dc/jenkins-pipeline-library@release/2.1.1']) _

// We choose to describe Docker image build directly in the Jenkinsfile instead of JePL2
// since this gives better control on the building process
// (e.g. which branches are allowed for docker image build)

def projectConfig

// function to remove built images
def docker_clean() {
    def dangling_images = sh(
	returnStdout: true,
	script: "docker images -f 'dangling=true' -q"
    )
    if (dangling_images) {
        sh(script: "docker rmi --force $dangling_images")
    }
}

pipeline {
    agent any

    environment {
        AI4OS_REGISTRY_CREDENTIALS = credentials('AIOS-registry-credentials')
        APP_DOCKERFILE = "Dockerfile"
    }

    stages {
        stage("Variable initialization") {
            steps {
                script {
                    checkout scm
                    withFolderProperties{
                        env.DOCKER_REGISTRY = env.AI4OS_REGISTRY
                        env.DOCKER_REGISTRY_ORG = env.AI4OS_REGISTRY_REPOSITORY
                        env.DOCKER_REGISTRY_CREDENTIALS = env.AI4OS_REGISTRY_CREDENTIALS
                    }
                    // get docker image name from metadata.json
                    meta = readJSON file: "metadata.json"
                    image_name = meta["sources"]["docker_registry_repo"].split("/")[1]
                    // define tag based on branch
                    image_tag = "${env.BRANCH_NAME == 'main' ? 'latest' : env.BRANCH_NAME}" 
                    env.DOCKER_REPO = env.DOCKER_REGISTRY_ORG + "/" + image_name + ":" + image_tag
                    env.DOCKER_REPO = env.DOCKER_REPO.toLowerCase()
                    println ("[DEBUG] Config for the Docker image build: $env.DOCKER_REPO, push to $env.DOCKER_REGISTRY")
                }
            }
        }

        // Application testing is based on JePL2. See .sqa directory
        stage('Application testing') {
            steps {
                script {
                    projectConfig = pipelineConfig()
                    buildStages(projectConfig)
                }
            }
        }

        stage("Docker image building & delivery") {
            when {
                anyOf {
                    branch 'main'
                    branch 'tokens'
                    branch 'release/*'
                    buildingTag()
                }
            }
            steps {
                script {
                    checkout scm
                    docker.withRegistry(env.DOCKER_REGISTRY, env.DOCKER_REGISTRY_CREDENTIALS){
                         def app_image = docker.build(env.DOCKER_REPO,
                                                      "--no-cache --force-rm --build-arg branch=${env.BRANCH_NAME} -f ${env.APP_DOCKERFILE} .")
                         app_image.push()
                    }
                }
            }
            post {
                failure {
                    docker_clean()
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

