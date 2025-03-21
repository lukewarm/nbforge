# NBForge EKS Deployment Guide

This guide explains how to deploy NBForge on Amazon Elastic Kubernetes Service (EKS) and set up the required services.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- `eksctl` CLI installed
- `kubectl` installed and configured
- `helm` CLI installed (optionally for deploying PostgreSQL and MinIO in the EKS cluster)

Login and set the default AWS profile
```bash
aws configure
```

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
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

eksctl create iamserviceaccount \
  --name nbforge-sa \
  --namespace default \
  --cluster nbforge-cluster \
  --attach-policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/nbforge-policy \
  --approve
```

4. Configure kubectl to point to the cluster:
```bash
aws eks update-kubeconfig --region us-east-1 --name nbforge-cluster
```

### Option 2: Using Custom RBAC (Alternative)

If you prefer more granular control, you can use the provided `rbac.yaml`:

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
  --engine-version 15.3 \
  --master-username nbforge \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20 \
  --storage-type gp2 \
  --publicly-accessible \
  --region us-east-1
```

2. Wait for the RDS instance to be created:
```bash
aws rds wait db-instance-available --db-instance-identifier nbforge-db
```

3. Get the RDS endpoint:
```bash
export RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier nbforge-db \
  --query "DBInstances[0].Endpoint.Address" \
  --output text)
```

4. Create a database:
```bash
# Install the PostgreSQL client if needed
sudo apt-get install -y postgresql-client || sudo yum install -y postgresql

# Create the nbforge database
PGPASSWORD=YOUR_PASSWORD psql \
  -h $RDS_ENDPOINT \
  -U nbforge \
  -c "CREATE DATABASE nbforge;"
```

5.Copy `../shared/backend.yaml.example` to `../shared/backend.yaml` and update its `backend-secrets` section:
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@$RDS_ENDPOINT:5432/nbforge"
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
helm repo update
helm install nbforge-db bitnami/postgresql \
  --set auth.database=nbforge \
  --set auth.username=nbforge \
  --set auth.password=YOUR_PASSWORD \
  --set primary.persistence.size=10Gi
```

2. Get the PostgreSQL password:
```bash
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default nbforge-db-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
echo $POSTGRES_PASSWORD
```

3. Copy `../shared/backend.yaml.example` to `../shared/backend.yaml` and update its `backend-secrets` section::
```yaml
DATABASE_URL: "postgresql://nbforge:YOUR_PASSWORD@nbforge-db-postgresql:5432/nbforge"
SECRET_KEY: <base64-encoded-secret-key>
AWS_ACCESS_KEY_ID: <base64-encoded-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
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

# Create access keys (make sure to generate HMAC key)
aws iam create-access-key --user-name nbforge-storage > nbforge-credentials.json
cat nbforge-credentials.json
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
  --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/nbforge-s3-policy
```

4. Update the `backend-secrets` in `backend.yaml`:
```yaml
# Extract values from nbforge-credentials.json
AWS_ACCESS_KEY_ID: <base64-encoded-access-key-id>
AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-access-key>
```

### Option 2: In-Cluster MinIO 

If you prefer running S3-compatible storage in the cluster:

1. Deploy MinIO using Helm:
```bash
helm repo add minio https://helm.min.io/
helm repo update
helm install nbforge-storage minio/minio \
  --set rootUser=admin \
  --set rootPassword=YOUR_PASSWORD \
  --set persistence.enabled=true \
  --set persistence.size=100Gi
```

2. Create a bucket:
```bash
# Port forward MinIO API port
kubectl port-forward svc/nbforge-storage 9000:9000 &

# Install MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
./mc config host add myminio http://localhost:9000 admin YOUR_PASSWORD
./mc mb myminio/nbforge-storage
```

3. Update the `backend-secrets` in `backend.yaml`:
```yaml
AWS_ACCESS_KEY_ID: <base64-encoded-admin>
AWS_SECRET_ACCESS_KEY: <base64-encoded-password>
S3_ENDPOINT_URL: "http://nbforge-storage:9000"
```

## Storage Integration with IRSA

One advantage of deploying NBForge on AWS is native S3 integration without requiring access keys. Using IAM Roles for Service Accounts (IRSA), we can securely access both ECR and S3 without storing credentials:

1. **Create an IAM policy for ECR and S3 access:**
```bash
cat << EOF > nbforge-access-policy.json
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
  --policy-name nbforge-access-policy \
  --policy-document file://nbforge-access-policy.json
```

2. **Create and configure the service account with IRSA:**
```bash
eksctl create iamserviceaccount \
    --name nbforge-sa \
    --namespace default \
    --cluster nbforge-cluster \
    --attach-policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/nbforge-access-policy \
    --approve \
    --override-existing-serviceaccounts
```

3. **Update the backend deployment to use this service account:**
```bash
# Add the following to the deployment spec in backend.yaml:
# spec:
#   template:
#     spec:
#       serviceAccountName: nbforge-sa
```

This setup eliminates the need for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your configuration, which is more secure and follows AWS best practices.

## Deployment

### Step 4: Set Up Container Registry (Optional)

You have two options for container registry:

#### Option A: Use Pre-built Images (Recommended)
If you're using the pre-built images from Docker Hub, you can skip this step and proceed to deployment.

#### Option B: Build and Push Custom Images to Amazon ECR

1. **Create ECR repositories:**
```bash
# Create repositories for NbForge images
aws ecr create-repository --repository-name nbforge/backend
aws ecr create-repository --repository-name nbforge/frontend
aws ecr create-repository --repository-name nbforge/notebook-runner
```

2. **Configure Docker to use ECR:**
```bash
# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1

# Configure Docker authentication
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

3. **Build and push the images:**
```bash
# Set version
export VERSION=1.0.0

# Build and push all images
docker buildx build --platform linux/amd64 -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/backend:$VERSION backend/
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/backend:$VERSION

docker buildx build --platform linux/amd64 -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/frontend:$VERSION frontend/
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/frontend:$VERSION

docker buildx build --platform linux/amd64 -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/notebook-runner:$VERSION notebook_runner/
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/notebook-runner:$VERSION
```

4. **Update the Kubernetes manifests:**
Edit `backend.yaml` and `frontend.yaml` to use your ECR images:
```yaml
# In backend.yaml and frontend.yaml, update the image field:
image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/backend:$VERSION  # for backend
image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/frontend:$VERSION  # for frontend
```

5. **Update the notebook runner configuration:**
Edit `backend-config` in `backend.yaml` to point to your custom notebook runner image:
```yaml
NOTEBOOK_RUNNER_IMAGE: "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nbforge/notebook-runner:$VERSION"
```

### Step 5: Install the AWS Load Balancer Controller

The AWS Load Balancer Controller is required for the ALB Ingress:

```bash
# Create an IAM policy for the ALB controller
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam-policy.json

# Create a service account for the ALB controller
eksctl create iamserviceaccount \
  --cluster=nbforge-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# Install the ALB controller using Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=nbforge-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

### Step 6: Deploy the Deployments and Services

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

3. Verify the deployment:
```bash
kubectl get pods
kubectl get services
```

### Step 7: Configure DNS and SSL with ALB Ingress

1. **Prepare an ACM certificate for your domain:**
```bash
# Request a certificate (you'll need to verify domain ownership)
aws acm request-certificate \
  --domain-name nbforge.example.com \
  --validation-method DNS

# Get the certificate ARN for use in the ingress
export CERT_ARN=$(aws acm list-certificates --query "CertificateSummaryList[?DomainName=='nbforge.example.com'].CertificateArn" --output text)
echo "Your certificate ARN is: $CERT_ARN"
```

2. **Update the certificate ARN in ingress-eks.yaml:**
Open `ingress-eks.yaml` and update the `alb.ingress.kubernetes.io/certificate-arn` annotation with your certificate ARN.

3. **Apply the Ingress YAML:**
```bash
# Before applying, update the host and certificate values in ingress-eks.yaml
# - Update "host: nbforge.example.com" to your actual domain
# - Update the certificate-arn annotation with your actual certificate ARN

# Apply the ingress configuration
kubectl apply -f ingress-eks.yaml
```

4. **Get the ALB DNS name:**
```bash
# Wait for the ALB to be provisioned (may take 2-5 minutes)
kubectl get ingress nbforge-ingress --watch

# Once the ALB is provisioned, capture its DNS name
export ALB_DNS_NAME=$(kubectl get ingress nbforge-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "Your ALB DNS name is: $ALB_DNS_NAME"
```

5. **Configure DNS in your provider (e.g., Cloudflare):**
   - Log in to your DNS provider account
   - Create a CNAME record pointing from your domain (nbforge.example.com) to the ALB DNS name
   - DNS settings example for Cloudflare:
     - Type: CNAME
     - Name: nbforge (or your subdomain)
     - Target: $ALB_DNS_NAME
     - Proxy status: DNS only initially, can be proxied later

6. **Understanding the ALB Ingress Components:**

   - **AWS Load Balancer Controller**: Creates and manages AWS Application Load Balancers based on Kubernetes Ingress resources
   
   - **ACM Certificate**: Provides SSL/TLS termination for secure HTTPS connections
   
   - **Target Groups**: Automatically created for each service backend
   
   - **Important Annotations**:
     - `kubernetes.io/ingress.class: alb`: Uses the AWS ALB ingress controller
     - `alb.ingress.kubernetes.io/scheme: internet-facing`: Makes the ALB accessible from the internet
     - `alb.ingress.kubernetes.io/target-type: ip`: Routes traffic to pod IPs
     - `alb.ingress.kubernetes.io/listen-ports`: Configures HTTP/HTTPS ports
     - `alb.ingress.kubernetes.io/actions.ssl-redirect`: Redirects HTTP to HTTPS
     - `alb.ingress.kubernetes.io/certificate-arn`: Specifies the ACM certificate to use

7. **Verify HTTPS Access:**
   Once DNS propagation is complete, you should be able to access your site securely:
   ```
   https://nbforge.example.com
   ```

### Step 8: Set Up the First Admin Account

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

### Step 9: Security Improvements

In the steps above, we run the server deployments and jobs using the default service account or a custom service account with broad permissions. For production environments, it's recommended to:

1. **Use dedicated service accounts for different components:**
```bash
# Create separate service accounts
kubectl create serviceaccount backend-sa
kubectl create serviceaccount frontend-sa
kubectl create serviceaccount notebook-runner-sa

# Apply more granular RBAC
kubectl apply -f fine-grained-rbac.yaml
```

2. **Update deployments to use these service accounts:**
```bash
# Edit the deployment files or use kubectl patch
kubectl patch deployment backend -p '{"spec":{"template":{"spec":{"serviceAccountName":"backend-sa"}}}}'
kubectl patch deployment frontend -p '{"spec":{"template":{"spec":{"serviceAccountName":"frontend-sa"}}}}'
```

3. **Consider using AWS Security Groups for Pods:**
```bash
# Enable SecurityGroups for Pods
aws eks update-cluster-config \
    --name nbforge-cluster \
    --region $AWS_REGION \
    --resources-vpc-config securityGroupIds=sg-12345,subnetIds=subnet-12345,subnet-67890

# Then use the securityGroups annotation in pod specs
```

4. **Set up Security Policies:**
```bash
# Apply pod security policies
kubectl apply -f pod-security-policies.yaml  # create this policy yourself following the best practice
```
