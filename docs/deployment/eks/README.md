# NBForge EKS Deployment Guide

This guide explains how to deploy NBForge on Amazon Elastic Kubernetes Service (EKS) and set up the required services.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- `eksctl` CLI installed
- `kubectl` installed and configured

## Service Account Setup

For EKS deployments, you have two options for service account configuration:

### Option 1: Using IAM Roles for Service Accounts (IRSA) (Recommended)

1. Create an EKS cluster with OIDC provider:
```bash
eksctl create cluster \
  --name nbforge-cluster \
  --region us-east-1 \
  --with-oidc
```

2. Create an IAM policy for the service account:
```bash
cat << EOF > nbforge-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters",
                "eks:AccessKubernetesApi"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam create-policy \
  --policy-name nbforge-policy \
  --policy-document file://nbforge-policy.json
```

3. Create a service account with the IAM role:
```bash
eksctl create iamserviceaccount \
  --name nbforge-sa \
  --namespace default \
  --cluster nbforge-cluster \
  --attach-policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/nbforge-policy \
  --approve
```

This approach is simpler and follows AWS best practices. The `rbac.yaml` file is not critical in this case as the service account permissions are managed at the AWS level.

### Option 2: Using Custom RBAC (Alternative)

If you prefer more granular control, you can still use the provided `rbac.yaml`:

```bash
kubectl apply -f rbac.yaml
```

## Database Setup

### Option 1: Amazon RDS (Recommended)

1. Create an RDS instance:
```bash
aws rds create-db-instance \
  --db-instance-identifier nbforge-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username nbforge \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

2. Create a database:
```bash
aws rds-data execute-statement \
  --resource-arn arn:aws:rds:us-east-1:YOUR_ACCOUNT_ID:cluster:nbforge-db \
  --database nbforge \
  --secret-arn YOUR_SECRET_ARN \
  --sql "CREATE DATABASE nbforge;"
```

3. Update the `backend-secrets` in `backend.yaml`:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db.YOUR_REGION.rds.amazonaws.com:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
ENV: "production"
CORS_ORIGINS: "https://nbforge.example.com"
```

### Option 2: In-Cluster PostgreSQL

If you prefer running PostgreSQL in the cluster:

1. Deploy PostgreSQL using Helm:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install nbforge-db bitnami/postgresql \
  --set auth.database=nbforge \
  --set auth.username=nbforge \
  --set auth.password=YOUR_PASSWORD
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

### Option 1: Amazon S3 (Recommended)

1. Create an S3 bucket:
```bash
aws s3api create-bucket \
  --bucket nbforge-storage \
  --region us-east-1
```

2. Create an IAM user for S3 access:
```bash
aws iam create-user --user-name nbforge-storage

# Create access keys
aws iam create-access-key --user-name nbforge-storage
```

3. Create and attach an IAM policy:
```bash
cat << EOF > s3-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::nbforge-storage",
                "arn:aws:s3:::nbforge-storage/*"
            ]
        }
    ]
}
EOF

aws iam create-policy \
  --policy-name nbforge-s3-policy \
  --policy-document file://s3-policy.json

aws iam attach-user-policy \
  --user-name nbforge-storage \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/nbforge-s3-policy
```

4. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
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
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
```

## Storage Integration

One advantage of deploying NBForge on AWS is native S3 integration without requiring access keys. Using IAM Roles for Service Accounts (IRSA), we can securely access both ECR and S3 without storing credentials:

1. **Create an IAM policy for ECR and S3 access:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ],
            "Resource": "arn:aws:ecr:us-east-1:$AWS_ACCOUNT_ID:repository/nbforge/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-nbforge-bucket",
                "arn:aws:s3:::your-nbforge-bucket/*"
            ]
        }
    ]
}
```

2. **Create and configure the service account with IRSA:**
```bash
eksctl create iamserviceaccount \
    --name nbforge-sa \
    --namespace default \
    --cluster nbforge-cluster \
    --attach-policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/nbforge-policy \
    --approve
```

This setup eliminates the need for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your configuration.

## Deployment

### Step 4: Set Up Container Registry (Optional)

You have two options for container registry:

#### Option A: Use Pre-built Images (Recommended)
If you're using the pre-built images from Docker Hub, you can skip this step and proceed to deployment.

#### Option B: Build and Push Custom Images to Amazon ECR

1. **Create ECR repository:**
```bash
# Create a single repository for all NbForge images
aws ecr create-repository --repository-name nbforge
```

2. **Configure Docker to use ECR:**
```bash
# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Configure Docker authentication
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

3. **Build and push the images:**
```bash
# Build and push all images
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/backend:$VERSION -f backend/Dockerfile .
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/backend:$VERSION

docker build -t $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/frontend:$VERSION -f frontend/Dockerfile .
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/frontend:$VERSION

docker build -t $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/notebook-runner:$VERSION -f notebook-runner/Dockerfile .
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/notebook-runner:$VERSION
```

4. **Update the Kubernetes manifests:**
Edit `backend.yaml` and `frontend.yaml` to use your ECR images:
```yaml
# In backend.yaml and frontend.yaml, update the image field:
image: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/backend:$VERSION  # for backend
image: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/frontend:$VERSION  # for frontend
```

5. **Update the notebook runner configuration:**
Edit `backend-secrets` in `backend.yaml` to point to your custom notebook runner image:
```yaml
NOTEBOOK_RUNNER_IMAGE: "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nbforge/notebook-runner:$VERSION"
```

6. **Configure IRSA for ECR access:**
```bash
# Create an IAM policy for ECR access
cat << EOF > ecr-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ],
            "Resource": "arn:aws:ecr:us-east-1:$AWS_ACCOUNT_ID:repository/nbforge/*"
        }
    ]
}
EOF

# Create the IAM policy
aws iam create-policy \
    --policy-name nbforge-ecr-policy \
    --policy-document file://ecr-policy.json

# Create a service account with the IAM role
eksctl create iamserviceaccount \
    --name nbforge-sa \
    --namespace default \
    --cluster nbforge-cluster \
    --attach-policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/nbforge-ecr-policy \
    --approve

# Update the service account in the deployments
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"serviceAccountName":"nbforge-sa"}}}}'
kubectl patch deployment frontend -p '{"spec":{"template":{"spec":{"serviceAccountName":"nbforge-sa"}}}}'
```

### Step 5: Configure DNS and SSL

1. **Get the external hostname:**
```bash
# Get the external hostname of the ingress controller
export EXTERNAL_HOSTNAME=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
```

2. **Configure DNS in Cloudflare:**
   - Note: We use Cloudflare as an example. Please change the configuration for your DNS provider accordingly.

   - Log in to your Cloudflare account
   - Select your domain
   - Go to DNS > Records
   - Add a CNAME record:
     - Name: nbforge (or your preferred subdomain)
     - Target: $EXTERNAL_HOSTNAME
     - Proxy status: Proxied (orange cloud)

3. **Create SSL certificate:**
```bash
# Create an SSL certificate using AWS Certificate Manager
aws acm request-certificate \
  --domain-name nbforge.example.com \
  --validation-method DNS

# Get the certificate ARN
export CERT_ARN=$(aws acm list-certificates --query 'CertificateSummaryList[?DomainName==`nbforge.example.com`].CertificateArn' --output text)

# Update ingress-eks.yaml with the certificate ARN
```

### Step 6: Deploy the Application

1. Apply the Kubernetes manifests:
```bash
cp backend.yaml.example backend.yaml
```
Adjust the configruations in `backend.yaml`, `frontend.yaml` and `ingress-eks.yaml`

```bash
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress-eks.yaml
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
