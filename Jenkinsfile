pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "anujkapile/devops-hub"
        K3S_INSTANCE = "172.31.4.204"
    }
    
    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Anujkapile/Anuj_Devops-utility-hub.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -f Docker/Dockerfile .'
                sh 'docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest'
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}'
                    sh 'docker push ${DOCKER_IMAGE}:latest'
                }
            }
        }
        
        stage('Deploy to K3s') {
            steps {
                sshagent(['k3s-instance']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no ubuntu@${K3S_INSTANCE} \
                    "kubectl rollout restart deployment/devops-hub -n devops-hub"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Deployment Successful'
        }
        failure {
            echo '❌ Deployment Failed!'
        }
    }
}
