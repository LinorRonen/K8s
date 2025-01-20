pipeline {
    agent {
        label 'general'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Pylint') {
            steps {
                script {
                    sh '''
                    pylint --fail-under 5 --disable=E0401 app.py
                    '''
                }
            }
        }
        stage('Build Image') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'VISUAL_CROSSING_TOKEN', variable: 'VISUAL_CROSSING_TOKEN')]) {
                        sh """
                        docker build --build-arg VISUAL_CROSSING_TOKEN=$VISUAL_CROSSING_TOKEN \
                        -f weather_app.dockerfile \
                        -t linorg/weather-application:${env.BUILD_NUMBER} .
                        """
                    }
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    sh """
                    docker rm -f weather-application-test || true
                    docker run -d --name weather-application-test -p 5002:5000 linorg/weather-application:${env.BUILD_NUMBER}
                    sleep 5
                    python3 tests/app_is_reachable.py || (docker logs weather-application-test && exit 1)
                    docker stop weather-application-test
                    docker rm weather-application-test
                    """
                }
            }
        }
        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'DOCKERHUB-CREDENTIALS', 
                                                  usernameVariable: 'DOCKER_USER', 
                                                  passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        sh """
                        docker login -u $DOCKER_USER -p $DOCKER_PASS
                        docker push linorg/weather-application:${env.BUILD_NUMBER}
                        """
                    }
                }
            }
        }
        stage('Deploy on EC2') {
            steps {
                script {
                    sh """
                    ssh -o StrictHostKeyChecking=no -i /home/ubuntu/.ssh/weather-app.pem ec2-user@172.31.40.4 \
                    "sudo systemctl start docker || true && \
                    sudo docker pull linorg/weather-application:${env.BUILD_NUMBER} && \
                    sudo docker stop weather-app || true && \
                    sudo docker rm weather-app || true && \
                    sudo docker run -d --name weather-app -p 80:5000 linorg/weather-application:${env.BUILD_NUMBER}"
                    """
                }
            }
        }
    }
    post {
        success {
            script {
                def slackChannel = "C081L4V40SJ"  
                def message = "Build #${env.BUILD_NUMBER} - SUCCESS: ${currentBuild.fullDisplayName}"
                
                slackSend(
                    channel: slackChannel, 
                    message: message, 
                    tokenCredentialId: 'SLACK-WEATHERAPP-TOKEN'
                )
            }
        }
        failure {
            script {
                def slackChannel = "C081C7BKFF1"  
                def message = "Build #${env.BUILD_NUMBER} - FAILURE: ${currentBuild.fullDisplayName}"
                
                slackSend(
                    channel: slackChannel, 
                    message: message, 
                    tokenCredentialId: 'SLACK-WEATHERAPP-TOKEN'
                )
            }
        }
    }
}
