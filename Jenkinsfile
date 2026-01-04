pipeline {
  agent any

  environment {
    // This MUST be a path that exists on the Docker HOST (your WSL path)
    HOST_PROJECT_DIR = "/mnt/p/logops-dashboard/logops-dashboard"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Tests') {
      steps {
        sh '''
          docker run --rm \
            -v "${HOST_PROJECT_DIR}":/app -w /app \
            python:3.11-slim \
            bash -lc "pip install -r requirements.txt && pytest -q"
        '''
      }
    }

    stage('Build & Deploy') {
      steps {
        sh '''
          # Use docker/compose container so we don't need compose inside Jenkins
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${HOST_PROJECT_DIR}":/work -w /work \
            docker/compose:1.29.2 down || true

          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${HOST_PROJECT_DIR}":/work -w /work \
            docker/compose:1.29.2 up --build -d

          sleep 3
          curl -f http://host.docker.internal:8080/health
        '''
      }
    }
  }
}
