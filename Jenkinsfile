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
      set -e

      echo "Finding requirements.txt..."
      REQ_PATH="$(find . -maxdepth 3 -name requirements.txt -print -quit)"
      if [ -z "$REQ_PATH" ]; then
        echo "❌ requirements.txt not found!"
        echo "Workspace contents:"
        ls -la
        exit 1
      fi

      APP_DIR="$(dirname "$REQ_PATH")"
      echo "Using APP_DIR=$APP_DIR"
      ls -la "$APP_DIR"

      docker run --rm \
        -v "$WORKSPACE":/repo \
        -w "/repo/$APP_DIR" \
        python:3.11-slim \
        bash -lc "pip install -r requirements.txt && pytest -q"
    '''
  }
}


    stage('Build & Deploy') {
  steps {
    sh '''
      set -e

      REQ_PATH="$(find . -maxdepth 3 -name requirements.txt -print -quit)"
      APP_DIR="$(dirname "$REQ_PATH")"
      echo "Using APP_DIR=$APP_DIR"

      docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$WORKSPACE":/repo \
        -w "/repo/$APP_DIR" \
        docker/compose:1.29.2 -p logops down || true

      docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$WORKSPACE":/repo \
        -w "/repo/$APP_DIR" \
        docker/compose:1.29.2 -p logops up --build -d

      echo "Waiting for host health..."
      for i in $(seq 1 30); do
        if curl -fsS http://localhost:8080/health | grep -q "ok"; then
          echo "✅ Health check OK"
          exit 0
        fi
        sleep 1
      done

      echo "❌ Health check FAILED"
      docker ps
      docker logs logops_app_1 --tail 80 || true
      docker logs logops_nginx_1 --tail 80 || true
      exit 1
    '''
  }
}

  }
}

