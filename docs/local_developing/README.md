# NBForge Local Development and Testing

This guide provides step-by-step instructions for setting up a complete NBForge development environment on your local machine (Mac or Linux).

## Architecture Overview

When developing locally, you'll need the following components:

1. **PostgreSQL** - Database for storing application data
2. **MinIO** - S3-compatible storage for notebooks and results
3. **Backend** - FastAPI application for API endpoints
4. **Frontend** - Vue.js application for the user interface
5. **Notebook Runner** - Component for executing notebooks

You have two options for development:
- **Option 1**: Run PostgreSQL, MinIO, backend and frontend directly on your host (simplest for getting started)
- **Option 2**: Run PostgreSQL and MinIO on your host, and both backend and frontend in Minikube with Ingress. You must use this option for testing the complete Kubernetes deployment, including **executing notebooks**.

## Prerequisites

- Docker
- Python 3.10 or later with pyenv or Anaconda
- Node.js 16 or later
- npm or yarn
- Git
- Minikube (for Option 2)
- kubectl (for Option 2)

All these can be installed using `brew` on Macs.

## Option 1: Direct Local Development

This option is best for frontend and backend development when you don't need to test notebook execution.

### Step 1: Set Up PostgreSQL

```bash
# Create a Docker volume for persistent data
docker volume create nbforge-postgres-data

# Run PostgreSQL container
docker run -d \
  --name nbforge-postgres \
  -e POSTGRES_USER=nbforge \
  -e POSTGRES_PASSWORD=nbforge \
  -e POSTGRES_DB=nbforge \
  -p 5432:5432 \
  -v nbforge-postgres-data:/var/lib/postgresql/data \
  postgres:14
```

### Step 2: Set Up MinIO

```bash
# Create Docker volumes for MinIO
docker volume create nbforge-minio-data

# Run MinIO container
docker run -d \
  --name nbforge-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v nbforge-minio-data:/data \
  minio/minio server /data --console-address ":9001"
```

After MinIO starts:
1. Open http://localhost:9001 in your browser
2. Log in with minioadmin / minioadmin
3. Create a bucket named "nbforge"

### Step 3: Set Up and Run the Backend

```bash
cd backend

# Create a virtual environment with pyenv or Anaconda
pyenv virtualenv 3.10.0 nbforge-env
pyenv activate nbforge-env


# Install dependencies
pip install -r requirements.txt

# Copy `.env.example` to `.env` and make necessary adjustment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Set Up and Run the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy `.env.example` to `.env` and make necessary adjustment
cp .env.example .env

# Start the development server
npm run dev
```

### Step 5: Set Up the First Admin Account

After starting both the backend and frontend, you need to create the first admin account. You can do this in two ways:

**Using the create_superuser.py script:**
```bash
# Option 1: Create a new admin user (requires password)
python backend/scripts/create_superuser.py admin@example.com your_secure_password

# Option 2: Make an existing user an admin (no password needed)
python backend/scripts/create_superuser.py existing_user@example.com
```

After creating the admin account, you can:
1. Navigate to http://localhost:8080
2. Log in with your admin credentials
3. Access the admin panel at http://localhost:8080/admin

Navigate to http://localhost:8080 to test most of the nbforge web app functions, except submit executions. To end-to-end test the executions, please follow option 2 below.


## Option 2: Minikube Setup with Ingress

This option runs PostgreSQL and MinIO on your host machine while running both the backend and frontend in Minikube with an Ingress for unified access. 

### Step 1: Set Up PostgreSQL and MinIO

Follow Steps 1 and 2 from Option 1 to set up PostgreSQL and MinIO.

### Step 2: Start Minikube with Ingress

```bash
# install minikube with `brew install minikube`

# Start Minikube with enough resources and enable the ingress addon
minikube start --cpus 4 --memory 8192

# you only need to run the next commands once to set things up on your machine
minikube addons enable ingress  
# Make your host services accessible inside Minikube
echo "$(minikube ip) host.minikube.internal" | sudo tee -a /etc/hosts
# Add nbforge.local to your hosts file
echo 127.0.0.1 nbforge.local" | sudo tee -a /etc/hosts
```

**Important**: before proceeding to the next steps, run this command to this command sets up your shell so that any Docker commands you run will interact with the Docker daemon inside Minikube.

Note that the PostgreSQL and MinIO containers on run on your laptop's Docker engine - the one you usually use for building and running containers locally. (We can also run both inside of Minikube, which may be a cleaner solution. If you choose to do that, change the service url in the yaml files.)

The NBForge web app conterians run inside Minikube, which provides a small Kubernetes cluster on your machine. 
This setup lets you test parts of the app in a full Kubernetes environment while still using your regular Docker for database and storage services.

(You can of course choose to run PostgreSQL and MinIO in Minikube too, as long as 
you change the address for those service accordingly in the .env setting files.)

```bash
eval $(minikube docker-env)
```

### Step 3: Build and Load Docker Images

```bash
# Navigate to the project root
cd /path/to/nbforge

# Build backend image
cd backend
docker build -t nbforge/backend:latest .

# Build frontend image
cd ../frontend
docker build -t nbforge/frontend:latest .

# Build notebook runner
cd ../notebook_runner
docker build -t nbforge/notebook-runner:latest .
```

### Step 4: Deploy Backend and Frontend to Minikube

First copy `backend.yaml.example` to `backend.yaml`

```bash
cp backend.yaml.example backend.yaml
```

Make sure that you never commit any secretes into source control.

We now need to update the yaml files in this folder to match your settings, specifically the secrets.

Run the command below to get the base64 encoded string of the secrets, which you should enter into the yaml files.

```bash
# Update the secrets in backend.yaml with your encoded values
cd /path/to/nbforge/deployment_new/local
echo -n "postgresql://nbforge:nbforge@host.minikube.internal:5432/nbforge" | base64
echo -n "minioadmin" | base64  # For MinIO credentials
echo -n "dev-secret-key" | base64  # replace with your own value
echo -n "your-smtp-email-server-password" | base64  # optionally with the email set up
```

Edit the `backend.yaml` file and carefully review them. The config and secrets sections set the env variables for the servers. 
(They replace the roles of the .env files in this set up.)

```bash
# Deploy the backend and frontend
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress.yaml
kubectl apply -f rbac.yaml

# Wait for deployments to be ready
kubectl wait --for=condition=available deployment/backend --timeout=120s
kubectl wait --for=condition=available deployment/frontend --timeout=120s
```

To see the status and logs of the Minikube cluster to monitor and to debug, 
it is highly recommended that you could use the Minikube Dashboard by running

```bash
minikube dashboard
```

### Step 5: Access the Application

After the deployments are ready, follow these steps so that you can access NBForge in your browser.

```bash
# In a new terminal window
minikube tunnel
```

Then run
```bash
kubectl patch svc ingress-nginx-controller -n ingress-nginx \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

you can access your application at:

```
http://nbforge.local
```

All API requests from your frontend to the backend will be routed through the Ingress at `/api/v1/*`.

### Step 6: Set Up the First Admin Account

After the deployment is complete, you need to create the first admin account. You can do this in two ways:

**Using the create_superuser.py script:**
```bash
# Get the backend pod name
BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Option 1: Create a new admin user (requires password)
kubectl exec -it $BACKEND_POD -- python /app/scripts/create_superuser.py admin@example.com your_secure_password

# Option 2: Make an existing user an admin (no password needed)
kubectl exec -it $BACKEND_POD -- python /app/scripts/create_superuser.py existing_user@example.com
```

After creating the admin account, you can:
1. Navigate to http://nbforge.local
2. Log in with your admin credentials
3. Access the admin panel at http://nbforge.local/#/admin/users

### Step 7: Verify the Setup

1. **Check that everything is running:**
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

2. **Test the API endpoint directly:**
```bash
curl http://nbforge.local/api/v1/health
```

3. **Check backend logs:**
```bash
kubectl logs deployment/backend
```

4. **Check frontend logs:**
```bash
kubectl logs deployment/frontend
```

## Testing with Service Account Keys

Once your application is running in Minikube with Ingress, you can test API endpoints using service account keys:

1. **Create a service account:**
   - Navigate to http://nbforge.local
   - Log in with admin credentials
   - Go to Admin → Service Accounts
   - Create a new service account and save the API key

2. **Use the API key to test endpoints:**
```bash
# Replace YOUR_SERVICE_ACCOUNT_KEY with your actual key
curl -H "Authorization: Bearer YOUR_SERVICE_ACCOUNT_KEY" http://nbforge.local/api/v1/notebooks
```

## Testing the Notebook Runner

When running in Minikube, the notebook runner will be executed as a Kubernetes job:

1. **Execute the notebook** from the UI

2. **Check the job status:**

```bash
kubectl get jobs
```

4. **Check job logs:**
```bash
# Replace JOB_NAME with the actual job name from the above command
kubectl logs job/JOB_NAME
```

## Troubleshooting

1. **Cannot connect to host PostgreSQL or MinIO from Minikube**
   - Ensure `host.minikube.internal` is properly set up
   - Check your host firewall settings
   - Verify PostgreSQL accepts remote connections

2. **Images not found in Minikube**
   - Verify with `minikube image list | grep nbforge`
   - Rebuild and reload images if necessary

3. **Ingress not working**
   - Check Ingress status: `kubectl get ingress`
   - Verify the Ingress controller is running: `kubectl get pods -n ingress-nginx`
   - Check Ingress controller logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller`

4. **Cannot resolve nbforge.local**
   - Verify the hosts file entry is correct
   - Try using the Minikube IP directly as a test

5. **Jobs fail to execute**
   - Check job logs: `kubectl logs job/notebook-runner-JOBID`
   - Verify S3 credentials and endpoint
   - Ensure MinIO bucket exists 