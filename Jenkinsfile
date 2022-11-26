pipeline {
    agent any

    environment {
        DOCKER_IMAGE = ""
    }

    stages{
        stage("Test") {
            steps {
                script {
                    try {
                        sh "mv docker.env .env"
                        echo "Done read enviroment"
                    }
                    catch (err) {
                        echo err.getMessage()
                    }
                }
                sh "pip3 install -r requirements.txt"
                echo  "Done install"
            }
        }

        stage("Clear") {
            steps {
                script {
                    try {
                        sh "docker rm pbl6-goship-backend_web_1 -f"
                        sh "docker rmi pbl6-goship-backend_web -f"
                        sh 'docker rm /$(docker ps --filter status=exited -q)'

                    }
                    catch (err) {
                        echo err.getMessage()
                    }
                }
            }
        }

        stage("Build") {
            steps {
                sh "sudo docker-compose up -d"
            }
        }
    }

    post {
        success {
            echo "SUCCESSFUL"
        }
        failure {
            echo "FAILED"
        }
    }
}
