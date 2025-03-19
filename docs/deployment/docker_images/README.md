# Building and Configuring NBForge Docker Images

This guide explains how to build Docker images for the NBForge platform components and how to configure environment variables, with special attention to sensitive information.

## Repository Structure

NBForge consists of three main components, each with its own Docker image and Dockerfile located in its respective project folder:

- **Frontend**: Vue.js web interface (`/frontend/Dockerfile`)
- **Backend**: FastAPI application (`/backend/Dockerfile`)
- **Notebook Runner**: Python service for executing notebooks (`/notebook_runner/Dockerfile`)

## Prerequisites

- Docker installed (version 20.10.0 or later recommended)
- Git to clone the repository
- Access to the NBForge codebase

## Building Images

### Backend Image

```bash
# Navigate to the backend directory
cd backend

# Build the image
docker build -t nbforge/backend:latest .

# Optionally tag with a specific version
docker tag nbforge/backend:latest nbforge/backend:v1.0.0
```

The backend Dockerfile includes:
- Python 3.10 base image
- Required Python dependencies
- Configuration for running the FastAPI application

### Frontend Image

```bash
# Navigate to the frontend directory
cd frontend

# Build the image
docker build -t nbforge/frontend:latest .

# Optionally tag with a specific version
docker tag nbforge/frontend:latest nbforge/frontend:v1.0.0
```

The frontend Dockerfile includes:
- Multi-stage build with Node.js for building the Vue app
- Nginx for serving the built static files
- Runtime configuration through environment variables

### Notebook Runner Image

```bash
# Navigate to the notebook_runner directory
cd notebook_runner

# Build the image
docker build -t nbforge/notebook-runner:latest .

# Optionally tag with a specific version
docker tag nbforge/notebook-runner:latest nbforge/notebook-runner:v1.0.0
```

The notebook runner Dockerfile includes:
- Python base image with multiple Python versions (3.9, 3.10, 3.11, 3.12)
- Jupyter dependencies
- Papermill and nbconvert for notebook execution
- Configuration for parameter validation and output handling
