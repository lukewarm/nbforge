# Self-Hosted Deployment

This guide explains how to deploy NBForge on a self-hosted Kubernetes cluster.

## Prerequisites

- A running Kubernetes cluster
- `kubectl` installed and configured
- Access to a PostgreSQL database
- Access to S3-compatible storage (e.g., MinIO)

## Deployment Steps

1. **Configure kubectl**
   Ensure your kubeconfig is properly set up to access your cluster.

2. **Deploy the backend**
   ```bash
   kubectl apply -f ../minimal/backend.yaml
   ```

3. **Deploy the frontend**
   ```bash
   kubectl apply -f ../minimal/frontend.yaml
   ```

4. **Verify the deployment**
   ```bash
   kubectl get deployments
   kubectl get services
   ```

The backend service will automatically create notebook execution jobs using the job template defined in the backend service.

## 1. Prepare Your Kubernetes Cluster

For a basic self-hosted cluster, ensure:

```bash
# Check node status
kubectl get nodes

# Verify system pods are running
kubectl -n kube-system get pods
```

## 2. Set Up PostgreSQL (Optional)

If you don't have an external PostgreSQL server, you can deploy one on your cluster:

```bash
# Create a namespace for the database
kubectl create namespace database

# Deploy PostgreSQL using Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql \
  --namespace database \
  --set auth.username=nbforge \
  --set auth.password=YOUR_SECURE_PASSWORD \
  --set auth.database=nbforge
```

Create a Kubernetes secret with your database connection string:

```bash
# Get PostgreSQL service name
POSTGRES_HOST=$(kubectl get svc -n database postgresql -o jsonpath='{.spec.clusterIP}')

kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="postgresql://nbforge:YOUR_SECURE_PASSWORD@${POSTGRES_HOST}:5432/nbforge"
```

## 3. Set Up MinIO for S3-Compatible Storage (Optional)

If you don't have an external S3-compatible storage, you can deploy MinIO:

```bash
# Create a namespace for storage
kubectl create namespace storage

# Deploy MinIO using Helm
helm repo add minio https://charts.min.io/
helm repo update
helm install minio minio/minio \
  --namespace storage \
  --set accessKey=YOUR_ACCESS_KEY \
  --set secretKey=YOUR_SECRET_KEY \
  --set persistence.size=10Gi
```

Create a bucket for NBForge:

```bash
# Port-forward to access MinIO
kubectl -n storage port-forward svc/minio 9000:9000 &

# Install MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
./mc alias set myminio http://localhost:9000 YOUR_ACCESS_KEY YOUR_SECRET_KEY
./mc mb myminio/nbforge
```

Create Kubernetes secrets for the S3 credentials:

```bash
# Get MinIO service name
MINIO_HOST=$(kubectl get svc -n storage minio -o jsonpath='{.spec.clusterIP}')

kubectl create secret generic storage-secrets \
  --from-literal=S3_ENDPOINT="http://${MINIO_HOST}:9000" \
  --from-literal=S3_ACCESS_KEY=YOUR_ACCESS_KEY \
  --from-literal=S3_SECRET_KEY=YOUR_SECRET_KEY \
  --from-literal=S3_BUCKET=nbforge
```

## 4. Install Nginx Ingress Controller

```bash
# Install Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.0/deploy/static/provider/cloud/deploy.yaml

# Wait for the controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

## 5. Configure MetalLB (for Bare Metal Clusters)

If your cluster runs on bare metal and lacks a cloud provider with load balancer support:

```bash
# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml

# Wait for MetalLB to be ready
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

# Configure IP address pool (adjust IP range to match your network)
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

## 6. Deploy NBForge Components

Apply the minimal deployment configurations:

```bash
# Apply backend deployment
kubectl apply -f ../minimal/backend.yaml

# Apply frontend deployment
kubectl apply -f ../minimal/frontend.yaml
```

## 7. Deploy Ingress Configuration

```bash
# Apply the self-hosted ingress configuration
kubectl apply -f ingress-self-hosted.yaml
```

## 8. Set Up DNS and Access

For a production environment, set up DNS to point to your ingress IP:

```bash
# Get the ingress controller service external IP
kubectl -n ingress-nginx get service ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

For a local environment or testing, you can add entries to your `/etc/hosts` file:

```bash
# Replace IP_ADDRESS with the actual IP address
echo "IP_ADDRESS nbforge.local" | sudo tee -a /etc/hosts
```

## 9. Set Up Monitoring (Optional)

Install Prometheus and Grafana for monitoring:

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

## Troubleshooting

- **Issue**: Ingress controller not working
  - **Solution**: Check Nginx Ingress logs with `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`

- **Issue**: Services not accessible through MetalLB
  - **Solution**: Verify IP address pool configuration and network routing

- **Issue**: Database connection errors
  - **Solution**: Check PostgreSQL deployment and connection string in the backend secrets 