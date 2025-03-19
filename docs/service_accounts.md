# Service Account Management in NBForge

Service accounts allow external systems (like Airflow, CI/CD pipelines, or other automation tools) to authenticate with the NBForge API without using personal user credentials. This document explains how to create, manage, and use service accounts.

## What are Service Accounts?

Service accounts are non-human users that provide a way for external systems to authenticate with the NBForge API. They:

- Have their own API keys for authentication
- Are tracked separately from regular user accounts
- Can be disabled or have their keys rotated without affecting other users

## Managing Service Accounts

### Prerequisites

To manage service accounts, you need:

1. Administrator privileges in NBForge
2. An access token for an admin user, which can be obtained by logging in through the UI or using the authentication endpoints

### Creating a Service Account

Service accounts can be created through the Admin UI by an admin user. When creating a service account, you'll need to provide:

1. A unique name for the service account
2. An optional description to help identify its purpose

After creation, you'll be shown the API key for the service account. This key is only displayed once, so make sure to save it securely. If you lose the key, you'll need to delete the service account and create a new one.

## Using Service Accounts

### Authentication Headers

When making API calls using a service account, you need to include the `Authorization` header with the Bearer token:

```
Authorization: Bearer <api-key>
```

For example:

```bash
curl -X POST "http://your-api-url/api/v1/executions" \
     -H "Authorization: Bearer abcdef1234567890abcdef1234567890abcdef12" \
     -H "Content-Type: application/json" \
     -d '{
         "notebook_path": "notebooks/data_analysis.ipynb",
         "parameters": {
             "data_source": "sales_2023.csv",
             "analysis_type": "monthly"
         },
         "python_version": "3.10"
     }'
```

### Airflow Integration Example

Here's a complete example of how to use a service account with Airflow:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import requests
from datetime import datetime, timedelta

# Get API key from Airflow Variables
API_KEY = Variable.get("nbforge_api_key")
API_URL = Variable.get("nbforge_api_url")

def execute_notebook(**context):
    """Function to trigger notebook execution"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Data for notebook execution
    data = {
        "notebook_path": "notebooks/daily_report.ipynb",
        "parameters": {
            "date": context['ds'],  # Execution date from Airflow
            "report_type": "daily"
        },
        "python_version": "3.10"
    }
    
    # Call the API to create an execution
    response = requests.post(
        f"{API_URL}/api/v1/executions",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to create execution: {response.text}")
    
    execution = response.json()
    execution_id = execution["id"]
    
    # Store the execution ID as an XCom for later tasks
    context['ti'].xcom_push(key='execution_id', value=execution_id)
    
    return execution_id

# Define a DAG
with DAG(
    'nbforge_daily_report',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Run daily reporting notebook',
    schedule_interval='0 5 * * *',  # 5 AM every day
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    
    execute_task = PythonOperator(
        task_id='execute_notebook',
        python_callable=execute_notebook,
        provide_context=True,
    )
```

## Security Best Practices

1. **Use unique service accounts for different systems** - Don't share service accounts across different systems
2. **Rotate API keys regularly** - Reset API keys periodically as part of security maintenance by deleting and recreating service accounts
3. **Disable unused accounts** - If a service account is temporarily not needed, you can delete it and create a new one when needed
4. **Audit access** - Regularly review service accounts and check their last used timestamps to ensure they're still needed 