# NBForge GKE Deployment Guide

This guide explains how to deploy NBForge on Google Kubernetes Engine (GKE) and set up the required services.

## Prerequisites

- A Google Cloud project with billing enabled
- `gcloud` CLI installed and configured
- `kubectl` installed and configured
- Access to create GKE clusters and manage resources

Login and set the default project
```bash
gcloud auth login
gcloud config set gcp-project-name
```

## Service Account Setup

For GKE deployments, you have two options for service account configuration:

### Option 1: Using GKE's Default Service Account (Recommended)

1. Create a GKE cluster with Workload Identity enabled:

It may be simpler to do this on the Cloud Console UI. If unsure, you should create a Autopilot cluster. 

Alternatively, you can use gcloud command to create it.
```bash
gcloud container clusters create nbforge-cluster \
  --workload-pool=YOUR_PROJECT_ID.svc.id.goog \
  --region=us-central1
```

2. Grant the default service account necessary permissions:
```bash
# Get the default service account email
export SA_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:default" \
  --format="value(email)")

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/container.developer"
```

3. Configure kubectl to point to the cluster
```bash
gcloud container clusters get-credentials <CLUSTER_NAME> --zone <ZONE> --project <PROJECT_ID>
```

### Option 2: Using Custom RBAC (Alternative)

If you prefer more granular control, you can still use the provided `rbac.yaml`:

```bash
kubectl apply -f rbac.yaml
```

## Database Setup

### Option 1: Cloud SQL (Recommended)

1. Create a Cloud SQL instance:
```bash
gcloud sql instances create nbforge-db \
  --database-version=POSTGRES_15 \
  --cpu=1 \
  --memory=3840MB \
  --region=us-central1
```

2. Create a database and user:
```bash
gcloud sql databases create nbforge --instance=nbforge-db
gcloud sql users create nbforge \
  --instance=nbforge-db \
  --password=YOUR_PASSWORD
```

3. Get the connection details:
```bash
export DB_HOST=$(gcloud sql instances describe nbforge-db \
  --format="value(connectionName)")
```

4. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@/nbforge?host=/cloudsql/$DB_HOST"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
S3_ENDPOINT_URL: "https://storage.googleapis.com"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

### Option 2: In-Cluster PostgreSQL

If you prefer running PostgreSQL in the cluster:

1. Deploy PostgreSQL using Helm:
```bash
kubectl apply -f postgresql-db.yaml
```

2. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```


## Storage Setup

### Option 1: Google Cloud Storage (Recommended)

1. Create a GCS bucket:
```bash
gsutil mb gs://nbforge-storage
```

2. Create a service account for GCS access:
```bash
gcloud iam service-accounts create nbforge-storage \
  --display-name="NBForge Storage Account"

# Grant storage access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:nbforge-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

3. Create and copy the service account HMAC key:
```bash
gcloud storage hmac create \
  nbforge-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

4. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@/nbforge?host=/cloudsql/$DB_HOST"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-hmac-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-hmac-secret-key>
S3_ENDPOINT_URL: "https://storage.googleapis.com"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

### Option 2: In-Cluster MinIO

If you prefer running S3-compatible storage in the cluster:

1. Deploy MinIO using Helm:
```bash
helm repo add minio https://helm.min.io/
helm install nbforge-storage minio/minio \
  --set rootUser=admin \
  --set rootPassword=YOUR_PASSWORD
```

2. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

## Storage Integration Note

Currently, NBForge uses AWS S3-compatible API for storage by default, which requires HMAC credentials. 
If you want to avoid using HMAC key:

1. You can extend the storage service to use Google Cloud Storage natively. See the storage service documentation in 
   `/backend/app/services/storage/README.md` for details on implementing custom storage backends.
2. Once extended, you can use Workload Identity to access GCS without credentials, similar to how we access Artifact Registry.
3. The service account running the backend service will need the following roles:
   - `roles/artifactregistry.reader` for container images
   - `roles/storage.objectAdmin` for GCS access (when implemented)

This modification would provide a fully native GCP deployment without requiring HMAC keys to work in S3 compatible mode.

## Deployment

### Step 4: Set Up Container Registry (Optional)

You have two options for container registry:

#### Option A: Use Pre-built Images (Recommended)
If you're using the pre-built images from Docker Hub, you can skip this step and proceed to deployment. (Note: these images are not yet pushed to Docker Hub yet.)

#### Option B: Build and Push Custom Images to Google Artifact Registry

1. **Create an Artifact Registry repository:**
```bash
# Create repositories for NBForge images
gcloud artifacts repositories create nbforge-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for NbForge"
```

2. **Configure Docker to use Artifact Registry:**
```bash
# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

3. **Build and push the images:**
```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)
export VERSION=1.0.0

# Build and push all images
docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/backend:$VERSION backend/
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/backend:$VERSION

docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/frontend:$VERSION frontend/
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/frontend:$VERSION

docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/notebook-runner:$VERSION notebook_runner/
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/notebook-runner:$VERSION
```

4. **Update the Kubernetes manifests:**
Edit `backend.yaml` and `frontend.yaml` to use your Artifact Registry images:
```yaml
# In backend.yaml and frontend.yaml, update the image field:
image: us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/backend:$VERSION  # for backend
image: us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/frontend:$VERSION  # for frontend
```

5. **Update the notebook runner configuration:**
Edit `backend-config` in `backend.yaml` to point to your custom notebook runner image:
```yaml
NOTEBOOK_RUNNER_IMAGE: "us-central1-docker.pkg.dev/$PROJECT_ID/nbforge-repo/notebook-runner:$VERSION"
```

6. **Configure Workload Identity for Artifact Registry access:**
```bash
# Get the service account email
export SA_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:default" \
  --format="value(email)")

# Grant Artifact Registry Reader role to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.reader"

# Enable Workload Identity for the namespace
kubectl annotate serviceaccount default \
  iam.gke.io/gcp-service-account=$SA_EMAIL
```

### Step 5: Deploy the Deployments and Services

1. Apply the Kubernetes manifests:
Then modify the configurations according to your set up.
```bash
cp ../shared/backend.yaml.example ../shared/backend.yaml
```
Adjust the configruations in `backend.yaml`, `frontend.yaml`

```bash
kubectl apply -f ../shared/backend.yaml
kubectl apply -f ../shared/frontend.yaml
```

2. Apply the RBAC
```bash
kubectl apply -f rbac.yaml
```

3. Verify the deployment:
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

### Step 6: Configure DNS and SSL with GKE Ingress

1. **Apply the Ingress YAML first:**
```bash
# Before applying, update the host and domain values in ingress-gke.yaml
# - Update "host: nbforge.example.com" to your actual domain
# - Update "domains: - nbforge.com" to your actual domain

# Apply the ingress configuration
kubectl apply -f ingress-gke.yaml
```

2. **Get the external IP address from the GKE ingress:**
```bash
# Reserve a static IP
gcloud compute addresses create nbforge-ip --global

# Verify the IP has been reserved
gcloud compute addresses describe nbforge-ip --global

# Wait for the ingress to get an IP address (may take 2-5 minutes)
kubectl get ingress nbforge-ingress --watch

# Once an IP is assigned, capture it
export EXTERNAL_IP=$(kubectl get ingress nbforge-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Your External IP is: $EXTERNAL_IP"
```

3. **Configure DNS in Cloudflare:**
   - Log in to your Cloudflare account
   - Select your domain
   - Go to DNS > Records
   - Add an A record:
     - Name: nbforge (or your preferred subdomain)
     - IPv4 address: $EXTERNAL_IP
     - Proxy status: DNS only (gray cloud) initially, until certificate provisioning is complete
     - After certificate is provisioned, you can switch to Proxied (orange cloud)

4. **Check Certificate Provisioning Status:**
```bash
# Check the status of your managed certificate
kubectl get managedcertificate

# You can also check detailed status
kubectl describe managedcertificate nbforge-certificate
```

*Note: Certificate provisioning through GKE ManagedCertificates can take 15-60 minutes. During this time, the domain validation is performed, which requires your DNS to be properly configured. The certificate will only be issued after successful domain validation.*

5. **Understanding the Ingress Components:**

   - **GCE Ingress Controller**: The native GKE ingress controller that provisions Google Cloud Load Balancers
   
   - **ManagedCertificate Resource**: Automatically provisions and renews SSL certificates through Google-managed certificates
   
   - **FrontendConfig Resource**: Configures load balancer settings, including HTTPS redirection
   
   - **Important Annotations**:
     - `kubernetes.io/ingress.class: "gce"`: Uses GKE's native ingress instead of Nginx
     - `kubernetes.io/ingress.global-static-ip-name`: (Optional) References a reserved static IP
     - `networking.gke.io/managed-certificates`: Links to the ManagedCertificate resource
     - `networking.gke.io/v1beta1.FrontendConfig`: Links to the FrontendConfig for HTTPS redirection

6. **Verify HTTPS Access:**
   Once the certificate is provisioned (status: Active), you should be able to access your site securely:
   ```
   https://nbforge.example.com
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
1. Navigate to https://nbforge.example.com
2. Log in with your admin credentials
3. Access the admin panel at https://nbforge.example.com/#/admin/users

