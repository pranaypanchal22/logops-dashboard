pipeline {
  agent any

  environment {
    HOST_PROJECT_DIR = "/mnt/p/logops-dashboard/logops-dashboard"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Tests') {
      steps {
        sh '''
          docker run --rm -v "${HOST_PROJECT_DIR}":/app -w /app python:3.11-slim \
            bash -lc "pip install -r requirements.txt && pytest -q"
        '''
      }
    }

    stage('Build & Deploy') {
      steps {
        sh '''
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${HOST_PROJECT_DIR}":/work -w /work \
            docker/compose:1.29.2 down || true

          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${HOST_PROJECT_DIR}":/work -w /work \
            docker/compose:1.29.2 up --build -d

          echo "Waiting for nginx health..."
          for i in $(seq 1 20); do
            if docker exec work_nginx_1 wget -qO- http://localhost/health | grep -q "ok"; then
              echo "Health check OK"
              exit 0
            fi
            sleep 1
          done

          echo "Health check FAILED - dumping logs"
          docker ps
          docker logs work_app_1 --tail 80 || true
          docker logs work_nginx_1 --tail 80 || true
          exit 1
        '''
      }
    }
  }
}
