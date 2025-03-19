#!/bin/bash
set -e

# Create kubernetes namespace if it doesn't exist
kubectl create namespace nbforge 2>/dev/null || true

# Create MinIO bucket
mc config host add local http://localhost:9000 minioadmin minioadmin
mc mb local/nbforge --ignore-existing

# Create kubernetes secrets
kubectl create secret generic s3-credentials \
  --from-literal=access-key=minioadmin \
  --from-literal=secret-key=minioadmin \
  --namespace nbforge

# Apply RBAC
kubectl apply -f deployment/k8s/papermill-executor-rbac.yaml -n nbforge

# Build papermill executor image
docker build -t papermill-executor:latest -f papermill_app/Dockerfile papermill_app/

echo "Local development environment setup complete!" 