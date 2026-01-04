pipeline {
  agent any

  environment {
    PROJECT_DIR = "."
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Tests') {
      steps {
        sh '''
          cd ${PROJECT_DIR}
          docker run --rm -v "$PWD":/app -w /app python:3.11-slim \
            bash -lc "pip install -r requirements.txt && pytest -q"
        '''
      }
    }

    stage('Build & Deploy') {
      steps {
        sh '''
          cd ${PROJECT_DIR}

          # Bring down existing stack (ignore errors)
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD":/work -w /work \
            docker/compose:1.29.2 down || true

          # Build and start
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD":/work -w /work \
            docker/compose:1.29.2 up --build -d

          sleep 3
          curl -f http://host.docker.internal:8080/health
        '''
      }
    }
  }
}
