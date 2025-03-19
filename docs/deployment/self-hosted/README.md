# NBForge Self-Hosted Deployment Guide

This guide explains how to deploy NBForge on a self-hosted Kubernetes cluster and set up the required services.

## Prerequisites

- A Kubernetes cluster (version 1.20 or higher)
- `kubectl` installed and configured
- `helm` installed (for package management)
- Access to create and manage resources in the cluster

## Service Account Setup

For self-hosted deployments, you'll need to set up RBAC permissions for the service account:

1. Apply the RBAC configuration:
```bash
kubectl apply -f rbac.yaml
```

2. Verify the permissions:
```bash
kubectl auth can-i create pods --as=system:serviceaccount:default:default
```

## Database Setup

### Option 1: External PostgreSQL (Recommended)

1. Set up a PostgreSQL server outside the cluster:
   - Install PostgreSQL on a dedicated server
   - Configure network access and firewall rules
   - Create a database and user:
```sql
CREATE DATABASE nbforge;
CREATE USER nbforge WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE nbforge TO nbforge;
```

2. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@your-postgres-host:5432/nbforge"
```

### Option 2: In-Cluster PostgreSQL

1. Deploy PostgreSQL using Helm:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install nbforge-db bitnami/postgresql \
  --set auth.database=nbforge \
  --set auth.username=nbforge \
  --set auth.password=YOUR_PASSWORD \
  --set primary.persistence.size=10Gi \
  --set primary.persistence.storageClass=standard
```

2. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db:5432/nbforge"
```

## Storage Setup

### Option 1: External S3-Compatible Storage (Recommended)

1. Set up an S3-compatible storage service:
   - MinIO server on a dedicated machine
   - Ceph Object Gateway
   - Other S3-compatible storage solutions

2. Create a bucket and access credentials:
```bash
# Example using MinIO client
mc alias set myminio http://your-minio-server:9000 admin YOUR_PASSWORD
mc mb myminio/nbforge-storage
mc admin user add myminio nbforge YOUR_ACCESS_KEY YOUR_SECRET_KEY
```

3. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-access-key>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
S3_ENDPOINT_URL: "http://your-s3-server:9000"
```

### Option 2: In-Cluster MinIO

1. Deploy MinIO using Helm:
```bash
helm repo add minio https://helm.min.io/
helm install nbforge-storage minio/minio \
  --set rootUser=admin \
  --set rootPassword=YOUR_PASSWORD \
  --set persistence.size=100Gi \
  --set persistence.storageClass=standard
```

2. Create a bucket:
```bash
# Install MinIO client
kubectl run -i --tty --rm minio-client \
  --image=minio/mc \
  --restart=Never \
  --command -- /bin/sh

# Inside the pod
mc alias set myminio http://nbforge-storage:9000 admin YOUR_PASSWORD
mc mb myminio/nbforge-storage
```

3. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
```

## Ingress Setup

1. Install an Ingress Controller (if not already installed):
```bash
# Using Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx
```

2. Configure SSL/TLS:
   - Generate SSL certificates (e.g., using Let's Encrypt)
   - Create a Kubernetes secret:
```bash
kubectl create secret tls nbforge-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem
```

3. Update the `ingress.yaml` with your domain and SSL configuration.

## Deployment

### Step 4: Set Up Container Registry (Optional)

You have two options for container registry:

#### Option A: Use Pre-built Images (Recommended)
If you're using the pre-built images from Docker Hub, you can skip this step and proceed to deployment.

#### Option B: Use a Private Container Registry

1. **Set up your private registry:**
   - You can use any private container registry (e.g., Harbor, GitLab Container Registry, etc.)
   - Make sure your registry is accessible from your Kubernetes cluster

2. **Configure Docker to use your registry:**
```bash
# Login to your private registry
docker login your-registry.example.com
```

3. **Build and push the images:**
```bash
# Build and push all images
docker build -t your-registry.example.com/nbforge/backend:$VERSION -f backend/Dockerfile .
docker push your-registry.example.com/nbforge/backend:$VERSION

docker build -t your-registry.example.com/nbforge/frontend:$VERSION -f frontend/Dockerfile .
docker push your-registry.example.com/nbforge/frontend:$VERSION

docker build -t your-registry.example.com/nbforge/notebook-runner:$VERSION -f notebook-runner/Dockerfile .
docker push your-registry.example.com/nbforge/notebook-runner:$VERSION
```

4. **Update the Kubernetes manifests:**
Edit `backend.yaml` and `frontend.yaml` to use your registry images:
```yaml
# In backend.yaml and frontend.yaml, update the image field:
image: your-registry.example.com/nbforge/backend:$VERSION  # for backend
image: your-registry.example.com/nbforge/frontend:$VERSION  # for frontend
```

5. **Update the notebook runner configuration:**
Edit `backend-secrets` in `backend.yaml` to point to your custom notebook runner image:
```yaml
NOTEBOOK_RUNNER_IMAGE: "your-registry.example.com/nbforge/notebook-runner:$VERSION"
```

6. **Configure Kubernetes to pull from your registry:**
```bash
# Create a secret for registry authentication
kubectl create secret docker-registry registry-secret \
    --docker-server=your-registry.example.com \
    --docker-username=your-username \
    --docker-password=your-password \
    --docker-email=your-email@example.com

# Update the service account to use the secret
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "registry-secret"}]}'
```

7. **Verify registry access:**
```bash
# Test pulling an image from your registry
kubectl run test-pull --image=your-registry.example.com/nbforge/backend:$VERSION --image-pull-policy=Always
```

### Step 5: Configure DNS and SSL

1. **Get the external IP address:**
```bash
# Get the external IP of the ingress controller
export EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

2. **Configure DNS in Cloudflare:**
   - Log in to your Cloudflare account
   - Select your domain
   - Go to DNS > Records
   - Add an A record:
     - Name: nbforge (or your preferred subdomain)
     - IPv4 address: $EXTERNAL_IP
     - Proxy status: Proxied (orange cloud)

3. **Create SSL certificate:**
```bash
# Create a self-signed certificate (for testing)
kubectl create secret tls nbforge-tls \
  --key=tls.key \
  --cert=tls.crt

# For production, use Let's Encrypt with cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Create a ClusterIssuer for Let's Encrypt
cat << EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Step 6: Deploy the Application

1. Apply the Kubernetes manifests:
```bash
cp backend.yaml.example backend.yaml
```
Adjust the configruations in `backend.yaml`, `frontend.yaml` and `ingress.yaml`

```bash
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress.yaml
```

2. Verify the deployment:
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

### Step 7: Set Up the First Admin Account

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
1. Navigate to https://your-domain.com
2. Log in with your admin credentials
3. Access the admin panel at https://your-domain.com/#/admin/users
