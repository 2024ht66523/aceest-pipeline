pipeline {
    agent any

    environment {
        IMAGE_NAME = "indervijay/aceest-gym"
        TAG = "v2"
    }

    stages {

        stage('Checkout') {
            steps {
                git '<YOUR_GITHUB_REPO_URL>'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'pytest'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                bat 'C:\\sonar-scanner\\bin\\sonar-scanner.bat'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%TAG% .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                    bat 'docker push %IMAGE_NAME%:%TAG%'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl set image deployment/aceest-deployment aceest=%IMAGE_NAME%:%TAG%'
            }
        }
    }
}