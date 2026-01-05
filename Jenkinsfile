pipeline {
  agent any

  environment {
    PROJECT_NAME = "logops"
    COMPOSE_IMAGE = "docker/compose:1.29.2"
    HOST_PROJECT_DIR = "${WORKSPACE}"
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
          docker run --rm -v "$WORKSPACE":/app -w /app python:3.11-slim \
            bash -lc "pip install -r requirements.txt && pytest -q"
        '''
      }
    }

    stage('Build & Deploy') {
      steps {
        sh '''
          set -e

          # Bring stack down/up using docker-compose container (no docker compose plugin needed)
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$HOST_PROJECT_DIR":/work -w /work \
            $COMPOSE_IMAGE -p $PROJECT_NAME down || true

          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$HOST_PROJECT_DIR":/work -w /work \
            $COMPOSE_IMAGE -p $PROJECT_NAME up --build -d

          echo "Waiting for host health on http://localhost:8080/health ..."
          for i in $(seq 1 30); do
            if curl -fsS http://localhost:8080/health | grep -q "ok"; then
              echo "✅ Health check OK"
              exit 0
            fi
            sleep 1
          done

          echo "❌ Health check FAILED - dumping logs"
          docker ps || true
          docker logs ${PROJECT_NAME}_app_1 --tail 120 || true
          docker logs ${PROJECT_NAME}_nginx_1 --tail 120 || true
          exit 1
        '''
      }
    }
  }
}

