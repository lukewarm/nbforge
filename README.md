# NBForge: Notebook Execution Platform

<div align="center">
  <!-- <img src="docs/assets/nbforge-logo.png" alt="NBForge Logo" width="150" /> -->
  <p><strong>Execute, parameterize, and automate Jupyter notebooks at scale</strong></p>
  
  <p>
    <a href="https://nbforge.com">Website</a> •
    <a href="https://demo.nbforge.com">Live Demo</a> •
    <a href="https://github.com/yourusername/nbforge">GitHub</a>
  </p>
</div>

## What is NBForge?

NBForge is a platform that transforms Jupyter notebooks into powerful, production-ready reporting tools and data processing components. It enables:

- **Parameterized Execution**: Run notebooks with different input parameters without modifying the code
- **Execution API**: Trigger notebook runs programmatically via a RESTful API
- **Resource Control**: Specify CPU and memory requirements for each notebook
- **Execution Tracking**: Monitor all notebook runs with detailed logs and outputs
- **Service Account Integration**: Automate notebook execution from Airflow, CI/CD pipelines, or other systems

## 🚀 Try NBForge

Experience NBForge today:

- **Project Website**: Learn more about NBForge features and use cases at [https://nbforge.com](https://nbforge.com)
- **Demo Site**: Try our fully functional demo at [https://demo.nbforge.com](https://demo.nbforge.com)
  - Login and email services are disabled on the demo site. 
  - The demo user can access the [admin panel](https://demo.nbforge.com/#/admin/service-accounts).


## Key Features

### 🔄 Turn Notebooks into Interactive APIs

Convert any Jupyter notebook into an API endpoint by adding a parameters cell. NBForge automatically generates a user interface for parameter input and validates the parameters before execution.

```python
# Analysis date range
start_date: str = "2023-01-01"  # {"description": "Start date for analysis", "input_type": "date"}
end_date: str = "2024-01-01"  # {"description": "End date for analysis", "input_type": "date"}

# Visualization parameters
plot_type: str = "line"  # {"description": "Type of plot to generate", "input_type": "select", "options": ["line", "bar", "scatter"]}
metrics: List[str] = ["churn_rate", "retention"]  # {"description": "Metrics to plot", "input_type": "multiselect", "options": ["churn_rate", "retention", "acquisition", "revenue"]}
```

### 🔌 Integration with Data Pipelines

Connect NBForge to your existing data workflows using NBForge service accounts and the REST API:

- **Airflow / Dagster** integration for scheduled notebook execution

### 📊 Execution Tracking and History

Get detailed insights into every notebook execution:
- Full execution logs and outputs
- Parameter values used for each run
- Execution duration and status tracking

### 🔐 Enterprise-Ready

- **Service account management** for secure API access
- **OAuth2 integration possibilities** with Google, Okta, and other identity providers

## Getting Started

Follow the local developing guide to set up NBForge web servers on your computer, with optinally the full 
Kubernetes experience using Minikube. See the [Local Development Setup](docs/local_developing/README.md).

### Kubernetes Deployment

For production environments, we provide Kubernetes manifests for deploying NBForge:

- [GKE Deployment Guide](docs/deployment/gke/README.md)
- [EKS Deployment Guide](docs/deployment/eks/README.md)
- [Self-hosted Kubernetes Guide](docs/deployment/self-hosted/README.md)

## Documentation

- [Deployment Options](docs/deployment/README.md)
- [Notebook Specification](docs/notebook_specification.md)
- [Admin Guide](docs/admin_guide.md)
    - [Service Account Management](docs/service_accounts.md)
- Authentication
    - [Okta](docs/auth/okta-integration.md)
    - [Google OAuth](docs/auth/google-oauth-integration.md)
- Service Extensions
    - [Extend to other storage providers](docs/service-extensions/storage.md)
    - [Extending to email api providers](docs/service-extensions/email.md)

## Architecture

NBForge runs on Kubernetes consists of three main components:

1. **Frontend**: A Vue.js web application for notebook management and execution configuration
2. **Backend**: A FastAPI service that provides the REST API and orchestrates notebook execution
3. **Notebook Runner**: Containerized execution environment for running parameterized notebooks using the excellent [Papermill](https://github.com/nteract/papermill)

The platform is designed to be cloud-native, scalable, and extensible, with support for various storage backends, authentication providers, and execution engines.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 