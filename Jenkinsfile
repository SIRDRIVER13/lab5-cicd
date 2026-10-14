// Potok CI/CD dla aplikacji Task API (projekt wielogałęziowy w Jenkinsie)
//
// Strategia gałęzi:
//   feature/*  -> tylko CI: lint, build, testy jednostkowe
//   develop    -> CI + automatyczne wdrożenie na środowisko testowe
//   main       -> CI + środowisko testowe + ręczna akceptacja + produkcja

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }

    environment {
        IMAGE       = "task-api:${env.BRANCH_NAME.replaceAll('[^A-Za-z0-9_.-]', '-')}-${env.BUILD_NUMBER}"
        VERSION     = "1.0.${env.BUILD_NUMBER}-${env.BRANCH_NAME.replaceAll('[^A-Za-z0-9_.-]', '-')}"
        TEST_URL    = 'http://host.docker.internal:8081'
        PROD_URL    = 'http://host.docker.internal:8082'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty="Commit %h: %s (%an)"'
            }
        }

        stage('Lint (flake8)') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r requirements-dev.txt
                    flake8 app.py tests --count --statistics
                    echo "Analiza statyczna: brak uwag"
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t "$IMAGE" .'
                sh 'docker image ls task-api --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | head -5'
            }
        }

        stage('Unit tests') {
            steps {
                sh '. .venv/bin/activate && mkdir -p reports && pytest -v --junitxml=reports/unit.xml'
            }
            post {
                always { junit 'reports/unit.xml' }
            }
        }

        stage('Deploy: test') {
            when { anyOf { branch 'main'; branch 'develop' } }
            steps {
                sh '''
                    APP_IMAGE="$IMAGE" APP_PORT=8081 APP_ENV=test APP_VERSION="$VERSION" \
                      docker compose -p task-api-test up -d --no-build --wait
                    docker compose -p task-api-test ps
                '''
                sh '''
                    . .venv/bin/activate
                    BASE_URL="$TEST_URL" pytest -v -o addopts="" tests/integration --junitxml=reports/integration.xml
                '''
                sh 'curl -s "$TEST_URL/"'
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/integration.xml' }
            }
        }

        stage('Approve production') {
            when { branch 'main' }
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input message: "Wdrożyć wersję ${env.VERSION} na produkcję?", ok: 'Wdróż na produkcję'
                }
            }
        }

        stage('Deploy: production') {
            when { branch 'main' }
            steps {
                sh '''
                    APP_IMAGE="$IMAGE" APP_PORT=8082 APP_ENV=production APP_VERSION="$VERSION" \
                      docker compose -p task-api-prod up -d --no-build --wait
                    docker compose -p task-api-prod ps
                    curl -s "$PROD_URL/"
                '''
            }
        }
    }

    post {
        always {
            script {
                currentBuild.description = "${env.VERSION} (${currentBuild.currentResult})"
            }
        }
        success {
            echo "POWIADOMIENIE: pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} zakończony SUKCESEM (${env.VERSION})"
        }
        failure {
            echo "POWIADOMIENIE: pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} zakończony BŁĘDEM: ${env.BUILD_URL}"
        }
        aborted {
            echo "POWIADOMIENIE: wdrożenie ${env.VERSION} na produkcję zostało odrzucone lub przerwane"
        }
    }
}
