#!/bin/bash
set -e

# Check required environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$S3_BUCKET" ]; then
    echo "Error: Required environment variables not set"
    echo "Please set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET"
    exit 1
fi

# Create base64 encoded secrets
ACCESS_KEY_B64=$(echo -n "$AWS_ACCESS_KEY_ID" | base64)
SECRET_KEY_B64=$(echo -n "$AWS_SECRET_ACCESS_KEY" | base64)

# Create kubernetes namespace
kubectl create namespace nbforge 2>/dev/null || true

# Create S3 credentials secret
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: s3-credentials
  namespace: nbforge
type: Opaque
data:
  access-key: $ACCESS_KEY_B64
  secret-key: $SECRET_KEY_B64
EOF

# Apply RBAC
kubectl apply -f deployment/k8s/papermill-executor-rbac.yaml -n nbforge

# Build and push container images
docker build -t papermill-executor:latest -f papermill_app/Dockerfile papermill_app/
docker tag papermill-executor:latest $CONTAINER_REGISTRY/papermill-executor:latest
docker push $CONTAINER_REGISTRY/papermill-executor:latest

echo "Production environment setup complete!" 