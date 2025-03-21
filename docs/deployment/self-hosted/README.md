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
kubectl apply -f ..shared/rbac.yaml
```

2. Verify the permissions:
```bash
kubectl auth can-i create pods --as=system:serviceaccount:default:default
```

## Database Setup

### Option 1: External PostgreSQL (Recommended)

1. Set up a PostgreSQL server outside the cluster:
   - Install PostgreSQL on a dedicated server (version 13 or later recommended)
   - Configure network access and firewall rules to allow connections from your Kubernetes nodes
   - Create a database and user:
```sql
CREATE DATABASE nbforge;
CREATE USER nbforge WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE nbforge TO nbforge;
```

2. Test the connection from your local machine or one of the Kubernetes nodes:
```bash
psql -h YOUR_POSTGRES_HOST -U nbforge -d nbforge -c "SELECT version();"
```

3. Copy `../shared/backend.yaml.example` to `../shared/backend.yaml` and update `backend-config` and `backend-secrets`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@your-postgres-host:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-access-key>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
S3_ENDPOINT_URL: "http://your-s3-server:9000"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

### Option 2: In-Cluster PostgreSQL

1. Deploy PostgreSQL using Helm:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install nbforge-db bitnami/postgresql \
  --set auth.database=nbforge \
  --set auth.username=nbforge \
  --set auth.password=YOUR_PASSWORD \
  --set primary.persistence.size=10Gi \
  --set primary.persistence.storageClass=standard
```

2. Get the PostgreSQL password if you used a generated password:
```bash
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default nbforge-db-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
echo $POSTGRES_PASSWORD
```

3. Copy `../shared/backend.yaml.example` to `../shared/backend.yaml` and update `backend-config` and `backend-secrets`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db-postgresql:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-access-key>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

## Storage Setup

### Option 1: External S3-Compatible Storage (Recommended)

1. Set up an S3-compatible storage service:
   - [MinIO server](https://min.io/docs/minio/linux/operations/installation.html) on a dedicated machine
   - [Ceph Object Gateway](https://docs.ceph.com/en/quincy/radosgw/index.html)
   - Other S3-compatible storage solutions

2. Create a bucket and access credentials:
```bash
# Example using MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
./mc alias set myminio http://your-minio-server:9000 admin YOUR_PASSWORD
./mc mb myminio/nbforge-storage
./mc admin user add myminio nbforge YOUR_ACCESS_KEY YOUR_SECRET_KEY
./mc admin policy set myminio readwrite user=nbforge
```

3. Test the connection:
```bash
./mc ls myminio/nbforge-storage
```

4. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-access-key>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
S3_ENDPOINT_URL: "http://your-s3-server:9000"
S3_BUCKET_NAME: "nbforge-storage"
```

### Option 2: In-Cluster MinIO

1. Deploy MinIO using Helm:
```bash
helm repo add minio https://helm.min.io/
helm repo update
helm install nbforge-storage minio/minio \
  --set rootUser=admin \
  --set rootPassword=YOUR_PASSWORD \
  --set persistence.enabled=true \
  --set persistence.size=100Gi \
  --set persistence.storageClass=standard \
  --set resources.requests.memory=1Gi
```

2. Create a bucket:
```bash
# Port forward MinIO API port
kubectl port-forward svc/nbforge-storage 9000:9000 &

# Install MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
./mc alias set myminio http://localhost:9000 admin YOUR_PASSWORD
./mc mb myminio/nbforge-storage
```

3. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
S3_BUCKET_NAME: "nbforge-storage"
```

## Ingress Setup

### Set up Ingress Controller

1. Install an Ingress Controller (if not already installed):
```bash
# Using Helm to install Nginx Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.publishService.enabled=true
```

2. Wait for the ingress controller to be ready:
```bash
kubectl wait --namespace default \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

3. For bare metal clusters without built-in load balancer support, install MetalLB:
```bash
# Install MetalLB for bare metal clusters
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.9/config/manifests/metallb-native.yaml

# Wait for MetalLB to be ready
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

# Create an IP address pool for MetalLB (adjust IP range to match your network)
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250  # Replace with your IP range
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool
EOF
```

### Configure SSL/TLS

It is likely that your organization already has a standard practice of exposoing Kubernetes services on the intranet.
Follow that instruction instead if there's one.

1. Install cert-manager for automated SSL certificates (recommended for production):
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=90s

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

2. For development or testing, you can create a self-signed certificate:
```bash
# Generate a self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt -subj "/CN=nbforge.example.com"

# Create a TLS secret
kubectl create secret tls nbforge-tls \
  --key tls.key \
  --cert tls.crt
```

3. Update the TLS section in `ingress-self-hosted.yaml`:
```yaml
# Uncomment the tls section in ingress-self-hosted.yaml and update with your domain
```

## Deployment

### Step 4: Set Up Container Registry (Optional)

You have two options for container registry:

#### Option A: Use Pre-built Images (Recommended)
If you're using the pre-built images from Docker Hub, you can skip this step and proceed to deployment.

#### Option B: Use a Private Container Registry

1. **Set up your private container registry**
   There are several options for running your own container registry:
   - [Harbor](https://goharbor.io/) - Enterprise container registry
   - [Docker Registry](https://docs.docker.com/registry/) - Simple registry server
   - GitLab/GitHub Container Registry

   Example for a simple Docker Registry deployment:
   ```bash
   helm repo add twuni https://helm.twun.io
   helm repo update
   helm install docker-registry twuni/docker-registry \
     --set persistence.enabled=true \
     --set persistence.size=10Gi
   
   # Create basic authentication
   htpasswd -Bbn reguser password > ./htpasswd
   kubectl create secret generic registry-auth \
     --from-file=./htpasswd
   ```

2. **Configure Docker to use your registry:**
```bash
# Login to your private registry
docker login your-registry.example.com -u reguser -p password
```

3. **Build and push the images:**
```bash
# Set version and registry
export REGISTRY=your-registry.example.com
export VERSION=1.0.0

# Build and push all images
docker buildx build --platform linux/amd64 -t $REGISTRY/nbforge/backend:$VERSION backend/
docker push $REGISTRY/nbforge/backend:$VERSION

docker buildx build --platform linux/amd64 -t $REGISTRY/nbforge/frontend:$VERSION frontend/
docker push $REGISTRY/nbforge/frontend:$VERSION

docker buildx build --platform linux/amd64 -t $REGISTRY/nbforge/notebook-runner:$VERSION notebook_runner/
docker push $REGISTRY/nbforge/notebook-runner:$VERSION
```

4. **Update the Kubernetes manifests:**
Edit `backend.yaml` and `frontend.yaml` to use your registry images:
```yaml
# In backend.yaml and frontend.yaml, update the image field:
image: your-registry.example.com/nbforge/backend:$VERSION  # for backend
image: your-registry.example.com/nbforge/frontend:$VERSION  # for frontend
```

5. **Update the notebook runner configuration:**
Edit `backend-config` in `backend.yaml` to point to your custom notebook runner image:
```yaml
NOTEBOOK_RUNNER_IMAGE: "your-registry.example.com/nbforge/notebook-runner:$VERSION"
```

6. **Configure Kubernetes to pull from your private registry:**
```bash
# Create a secret for registry authentication
kubectl create secret docker-registry registry-creds \
    --docker-server=your-registry.example.com \
    --docker-username=reguser \
    --docker-password=password

# Update the service account to use the secret
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "registry-creds"}]}'
```

### Step 5: Deploy the Application

1. Apply the Kubernetes manifests:
```bash
cp ../shared/backend.yaml.example ../shared/backend.yaml
```
Adjust the configurations in `backend.yaml` and `frontend.yaml`

```bash
kubectl apply -f ../shared/backend.yaml
kubectl apply -f ../shared/frontend.yaml
```

2. Apply the RBAC
```bash
kubectl apply -f rbac.yaml
```

3. Apply the Ingress configuration:
```bash
# Update the host value in ingress-self-hosted.yaml to your domain
kubectl apply -f ingress-self-hosted.yaml
```

4. Verify the deployment:
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

### Step 6: Configure DNS

It is likely that your organization already has a standard practice of exposoing Kubernetes services on the intranet.
Follow that instruction instead if there's one.


1. **Get the external IP address:**
```bash
# Get the external IP of the ingress controller
export EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Your external IP is: $EXTERNAL_IP"
```

2. **Configure DNS in your provider:**
   - Log in to your DNS provider account
   - Create an A record pointing from your domain (nbforge.example.com) to the external IP
   - DNS settings example:
     - Type: A
     - Name: nbforge (or your subdomain)
     - Value: $EXTERNAL_IP
     - TTL: 5 minutes (for testing)

3. **For local testing without DNS:**
   You can add an entry to your `/etc/hosts` file:
   ```bash
   echo "$EXTERNAL_IP nbforge.example.com" | sudo tee -a /etc/hosts
   ```

4. **Test the DNS resolution:**
```bash
nslookup nbforge.example.com
curl -k https://nbforge.example.com
```

### Step 7: Set Up the First Admin Account

After the deployment is complete, you need to create the first admin account. You can do this in two ways:

**Using the create_superuser.py script:**
```bash
# Get the backend pod name
export BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Option 1: Create a new admin user (requires password)
kubectl exec -it $BACKEND_POD -- python /app/scripts/create_superuser.py admin@example.com your_secure_password

# Option 2: Make an existing user an admin (no password needed)
kubectl exec -it $BACKEND_POD -- python /app/scripts/create_superuser.py existing_user@example.com
```

After creating the admin account, you can:
1. Navigate to https://nbforge.example.com
2. Log in with your admin credentials
3. Access the admin panel at https://nbforge.example.com/#/admin/users

### Step 8: Security Improvements by Using Different Service Accounts for Each Service

1. **Use dedicated service accounts for different components:**
```bash
# Create separate service accounts
kubectl create serviceaccount backend-sa
kubectl create serviceaccount frontend-sa
kubectl create serviceaccount notebook-runner-sa

# Apply more granular RBAC
kubectl apply -f fine-grained-rbac.yaml  # create this file yourself
```

2. **Update deployments to use these service accounts:**
```bash
# Edit the deployment files or use kubectl patch
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"serviceAccountName":"backend-sa"}}}}'
kubectl patch deployment frontend -p '{"spec":{"template":{"spec":{"serviceAccountName":"frontend-sa"}}}}'
```
