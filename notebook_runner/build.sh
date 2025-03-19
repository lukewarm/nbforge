#!/bin/bash
set -e

# Build the notebook runner image
echo "Building notebook runner image..."
docker build -t nbforge/notebook-runner:latest .

# Push to registry if requested
if [ "$1" == "--push" ]; then
    echo "Pushing image to registry..."
    docker push nbforge/notebook-runner:latest
fi

echo "Build complete!" 