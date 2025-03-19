#!/bin/bash

set -e

# Check if Minikube is running
if ! minikube status &>/dev/null; then
  echo "Minikube is not running. Starting Minikube..."
  minikube start
fi

# Set the Docker environment to use Minikube's Docker daemon
echo "Setting up Docker environment for Minikube..."
eval $(minikube docker-env)

# Build the images
echo "Building backend image..."
cd ../../backend
docker build -t nbforge/backend:latest .

echo "Building notebook-runner image..."
cd ../notebook_runner
docker build -t nbforge/notebook-runner:latest .

# Reset Docker environment
eval $(minikube docker-env -u)

echo "Images successfully built and loaded into Minikube."
echo ""
echo "Next steps:"
echo "1. Ensure PostgreSQL and MinIO are running on your host machine"
echo "2. Create database and bucket:"
echo "   - PostgreSQL database: nbforge"
echo "   - MinIO bucket: nbforge"
echo "3. Deploy the backend to Minikube:"
echo "   kubectl apply -f backend.yaml"
echo "4. Get the backend service URL:"
echo "   minikube service backend-service --url"
echo ""
echo "For more details, refer to the LOCAL_DEVELOPMENT.md guide." 