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
      set -euxo pipefail

      # Copy SCM checkout (inside Jenkins container) to a HOST-mounted folder
      rm -rf /workspace/repo
      mkdir -p /workspace/repo
      cp -a . /workspace/repo

      echo "Contents in /workspace/repo:"
      ls -la /workspace/repo
      test -f /workspace/repo/requirements.txt

      docker run --rm \
        -v "/workspace/repo":/repo \
        -w /repo \
        python:3.11-slim \
        bash -lc "ls -la && test -f requirements.txt && pip install -r requirements.txt && pytest -q"
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
  -v "/workspace/repo":/work \
  -w /work \
  docker/compose:1.29.2 -p logops down || true

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "/workspace/repo":/work \
  -w /work \
  docker/compose:1.29.2 -p logops up --build -d


      echo "Waiting for health on host port 8080..."
for i in $(seq 1 30); do
  if docker run --rm --network host curlimages/curl:8.6.0 -fsS http://localhost:8080/health | grep -q ok; then
    echo "✅ Health check OK"
    exit 0
  fi
  sleep 1
done

echo "❌ Health check FAILED"
docker ps
docker logs logops_app_1 --tail 80 || true
docker logs logops_nginx_1 --tail 120 || true
exit 1

    '''
  }
}

  }
}

