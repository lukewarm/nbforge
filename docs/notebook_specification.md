# Notebook Specification

This document describes the format and requirements for notebooks that can be executed by the NBForge platform.

## File Format

Notebooks must be in the standard Jupyter Notebook format (`.ipynb`), which is a JSON document containing code cells, markdown cells, and metadata.

## Metadata Requirements

Notebooks should include metadata that helps the platform understand how to execute them. This metadata should be included in the notebook's metadata section under the `nbforge` key.

### Example Metadata Structure

```json
{
  "metadata": {
    "nbforge": {
      "name": "Example Analysis",
      "description": "This notebook performs an example analysis on the provided dataset",
      "tags": ["example", "analysis", "demo"],
      "python_version": "3.10",
      "requirements": {
        "pandas": ">=1.3.0",
        "matplotlib": ">=3.4.0",
        "scikit-learn": ">=1.0.0"
      },
      "resources": {
        "cpu_milli": 2000,
        "memory_mib": 4096
      }
    }
  }
}
```

### Metadata Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Human-readable name of the notebook | Yes |
| `description` | string | Brief description of what the notebook does | Yes |
| `tags` | array of strings | Tags for categorizing the notebook | No |
| `python_version` | string | Python version required (e.g., "3.9") | No |
| `requirements` | object | Dictionary of Python package requirements with version constraints | No |
| `resources` | object | Resource requirements for execution | No |

#### Resources Object

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `cpu_milli` | integer | CPU millicores to allocate | 1000 |
| `memory_mib` | integer | Memory in MiB to allocate | 2048 |

## Parameters

Notebooks can define parameters that can be provided at execution time. Parameters should be defined in the metadata of code cells using the `parameters` key.

### Parameter Specification

Parameters are defined in a code cell tagged with `parameters`. This follows the Papermill convention with NBForge enhancements. Parameters should be defined with type annotations, and can include additional metadata in JSON format as comments.

### Supported Parameter Types

NBForge supports the following parameter types:

| Python Type | Description | Example |
|-------------|-------------|---------|
| `str` | Text values | `model_name: str = "xgboost"` |
| `int` | Integer values | `iterations: int = 100` |
| `float` | Floating point values | `learning_rate: float = 0.01` |
| `bool` | Boolean values | `use_gpu: bool = False` |
| `List[T]` | Lists of specific types | `features: List[str] = ["age", "income"]` |
| `Dict[K, V]` | Dictionary | `config: Dict[str, str] = {"mode": "test"}` |
| `Optional[T]` | Optional parameters | `Optional[str] = None` |

### Parameter Customization via Comments

Parameters can be customized with additional metadata in JSON format as comments. This metadata controls how the parameter is presented in the UI and any validation rules.

#### Available Customization Options

| Option | Description | Example |
|--------|-------------|---------|
| `description` | Human-readable description | `"description": "Learning rate for gradient descent"` |
| `input_type` | UI input type | `"input_type": "select"` |
| `options` | Options for select/multiselect | `"options": ["xgboost", "random_forest", "nn"]` |
| `validation` | Validation rules | `"validation": {"min": 0, "max": 1}` |
| `default` | Default value | `"default": 0.01` |

#### Input Types

| Input Type | Description |
|------------|-------------|
| `text` | Standard text input (default for string) |
| `number` | Numeric input (default for int/float) |
| `date` | Date picker |
| `datetime` | Date and time picker |
| `checkbox` | Boolean checkbox (default for bool) |
| `select` | Dropdown selection |
| `multiselect` | Multiple selection dropdown (for lists) |
| `textarea` | Multi-line text input |

### Date Handling

Dates should be handled as follows:
1. Define date parameters as strings (`str`) with the `date` input type
2. Parse these strings into proper date objects in subsequent cells

This approach allows for flexible date input while maintaining proper type checking.

### Example Parameter Cell

```python
# Basic parameter types
model_name: str = "xgboost"  # {"description": "ML model to use", "input_type": "select", "options": ["xgboost", "random_forest", "neural_network"]}
learning_rate: float = 0.01  # {"description": "Learning rate", "validation": {"min": 0.0001, "max": 1.0}}
iterations: int = 100  # {"description": "Number of training iterations", "validation": {"min": 10}}
use_features: List[str] = ["age", "income", "tenure"]  # {"description": "Features to include in the model", "input_type": "multiselect", "options": ["age", "income", "tenure", "products", "location"]}
enable_early_stopping: bool = True  # {"description": "Enable early stopping during training"}

# Date parameters (defined as strings)
start_date: str = "2023-01-01"  # {"description": "Start date for analysis", "input_type": "date", "validation": {"min": "2020-01-01"}}
end_date: str = "2024-01-01"  # {"description": "End date for analysis", "input_type": "date"}

# Optional parameters
custom_config: Optional[Dict[str, str]] = None  # {"description": "Optional custom configuration"}
```

### Date Parsing Example

After defining date parameters as strings, they should be parsed in a subsequent cell:

```python
# Parse date strings into datetime objects
import pandas as pd
from datetime import datetime

# Parse using pandas for flexibility in accepted formats
start_date_dt = pd.to_datetime(start_date).date()
end_date_dt = pd.to_datetime(end_date).date()

# Alternatively, use datetime directly if format is known
# start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
# end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

# Validation can be done after parsing
if start_date_dt >= end_date_dt:
    raise ValueError("Start date must be before end date")
```

## Best Practices

1. **Idempotence**: Notebooks should be idempotent - running them multiple times with the same parameters should produce the same results.
2. **Error Handling**: Include proper error handling to provide meaningful error messages.
3. **Documentation**: Include markdown cells explaining the purpose and methodology of the notebook.
4. **Resource Efficiency**: Be mindful of resource usage, especially for large datasets.
5. **Parameterization**: Parameterize all variables that might need to change between runs.
6. **Parameter Validation**: Include validation for parameters, both in the metadata and with explicit checks in code.
7. **Default Values**: Provide sensible defaults for all parameters when possible. 