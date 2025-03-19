# Minimal Kubernetes Deployment

This directory contains the minimal Kubernetes manifests needed to deploy NBForge.

## Files

- `backend.yaml.example`: Example backend service deployment and configuration
- `frontend.yaml`: Frontend service deployment and configuration


## Configuration

Before deploying, copy the example configuration file and update with your actual values:

```bash
# Copy the example configuration
cp backend.yaml.example backend.yaml
```

Then update the following values in your new `backend.yaml` file:

- In `backend.yaml`: Update the database URL, S3 credentials, and JWT secret
- In `frontend.yaml`: Update the API URL if needed

## Deployment

Apply the configuration in the following order:

```bash
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
```

## Next Steps

After deploying these minimal components, you will need to:

1. Set up ingress or load balancers to expose the services
2. Configure authentication providers if needed
3. Create the initial admin user

See the Amazon EKS, Google GKE, or self hosted Kubernetes cluster guides for more details about these steps.
