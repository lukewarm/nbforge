# NBForge Deployment

This directory contains configurations and instructions for deploying NBForge on various Kubernetes environments, designed to be simple and adaptable to your infrastructure needs.

## Overview

NBForge is a scalable notebook execution platform that can be deployed on:
- Google Kubernetes Engine (GKE)
- Amazon Elastic Kubernetes Service (EKS)
- Self-hosted Kubernetes clusters
- Local development environments

Each deployment option includes configurations for:
- Frontend UI service
- Backend API service
- Notebook execution service
- Service networking and access

## Deployment Options

Choose the deployment option that matches your environment:

- [**Google Kubernetes Engine (GKE)**](gke/README.md) - Optimized for Google Cloud with built-in load balancing and GCP service integration
- [**Amazon EKS**](eks/README.md) - Configured for AWS with ALB/NLB support and integration with AWS services
- [**Self-hosted Kubernetes**](self-hosted/README.md) - For on-premises or custom Kubernetes clusters


4. Follow platform-specific configurations in the respective directory.

## Directory Structure

- `shared/` - Core deployment manifests shared across the three platform options
- Platform-specific directories: `gke/`, `eks/`, `self-hosted/`

