# FabRest

FabRest is a Python library designed to interact with Microsoft Fabric REST APIs, providing a convenient interface for managing and operating various Fabric resources such as workspaces, data pipelines, lakehouses, and more.

## Overview

FabRest aims to simplify the process of automating and managing Microsoft Fabric resources through its REST API. It offers a set of operators and API endpoints that allow developers and data engineers to create, update, delete, and monitor Fabric items programmatically.

## Features

- **Authentication**: Securely authenticate with Microsoft Fabric using all methods supported by `azure.identity` (such as `ClientSecretCredential`, `DefaultAzureCredential`, and `InteractiveBrowserCredential`), along with a custom `ResourceOwnerPasswordCredential` provided by this package for ROPC flow.
- **Resource Management**: Create, update, delete, and list resources like workspaces, lakehouses, data pipelines, and more.
- **Data Operations**: Manage data pipelines, run jobs, and handle data within Fabric environments.
- **Comprehensive API Coverage**: Access a wide range of Fabric REST API endpoints for detailed control over your data infrastructure.
- **Asynchronous Support**: Perform operations asynchronously for improved performance in concurrent environments.

## Installation

To install FabRest, you can use pip:

```bash
pip install fabrest
```

Alternatively, if you are working from the source code:

```bash
git clone https://github.com/billybillysss/fabrest.git
cd fabrest
pip install .
```

## Usage

Below are examples of how to use FabRest to manage resources in your Fabric environment. The examples are divided into authentication setup and specific operations for managing data pipelines, with both synchronous and asynchronous approaches for clarity.

### Authentication

FabRest supports all authentication methods provided by `azure.identity`, along with a custom credential class for specific use cases. Below are examples of different credential types you can use to authenticate with Microsoft Fabric:

**ClientSecretCredential**

This method is suitable for service principal authentication in automated workflows or applications.

```python
from azure.identity import ClientSecretCredential
from fabrest.operator.workspace import WorkspaceOperator

# Initialize the client with your credentials
credential = ClientSecretCredential(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
)

# Initialize a workspace operator
workspace_operator = WorkspaceOperator(
    id="your-workspace-id",
    credential=credential
)
```

**DefaultAzureCredential**

This method attempts to authenticate using multiple credential types in order, making it versatile for different environments (e.g., local development, CI/CD pipelines).

```python
from azure.identity import DefaultAzureCredential
from fabrest.operator.workspace import WorkspaceOperator

# Initialize the client with default credentials
credential = DefaultAzureCredential()

# Initialize a workspace operator
workspace_operator = WorkspaceOperator(
    id="your-workspace-id",
    credential=credential
)
```

**InteractiveBrowserCredential**

This method is useful for local development, prompting the user to authenticate via a browser.

```python
from azure.identity import InteractiveBrowserCredential
from fabrest.operator.workspace import WorkspaceOperator

# Initialize the client with interactive browser credentials
credential = InteractiveBrowserCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id"
)

# Initialize a workspace operator
workspace_operator = WorkspaceOperator(
    id="your-workspace-id",
    credential=credential
)
```

**ResourceOwnerPasswordCredential**

This custom credential class, created within the FabRest package, handles specific operations or resources in Microsoft Fabric that do not support service principal authentication and require user identity. It uses the Resource Owner Password Credential (ROPC) flow.

```python
from fabrest.api.auth import ResourceOwnerPasswordCredential
from fabrest.operator.workspace import WorkspaceOperator

# Initialize the client with ROPC credentials for user identity
credential = ResourceOwnerPasswordCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",
    username="your-username",
    password="your-password"
)

# Initialize a workspace operator
workspace_operator = WorkspaceOperator(
    id="your-workspace-id",
    credential=credential
)
```

### Managing Data Pipelines

#### Synchronous Operations

**Creating a Data Pipeline**

```python
from fabrest.operator.workspace import WorkspaceOperator
from azure.identity import ClientSecretCredential

# Initialize credentials and operator
credential = ClientSecretCredential(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
)
operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

# Create a data pipeline
pipeline_name = "test_pipeline"
response = operator.data_pipelines.create(payload={"displayName": pipeline_name})
pipeline_data = response.json()
pipeline_id = pipeline_data["id"]
print(f"Created pipeline with ID: {pipeline_id}")
```

**Listing Data Pipelines**

```python
# List all data pipelines in the workspace
pipelines = operator.data_pipelines.list()
for pipeline in pipelines:
    print(f"Pipeline: {pipeline['displayName']} (ID: {pipeline['id']})")
```

**Getting a Specific Data Pipeline**

```python
# Get details of a specific pipeline
pipeline_data = operator.data_pipelines.get(id=pipeline_id)
print(f"Retrieved pipeline: {pipeline_data['displayName']} (ID: {pipeline_data['id']})")
```

**Updating a Data Pipeline Name**

```python
# Update pipeline name
updated_name = pipeline_name + "_updated"
response = operator.data_pipelines.update(id=pipeline_id, payload={"displayName": updated_name})
updated_data = response.json()
print(f"Updated pipeline name to: {updated_data['displayName']}")
```

**Updating a Data Pipeline Definition**

```python
import json
from fabrest.utils.functions import encode_base64

# Update pipeline definition with a new activity
update_def_payload = {
    "properties": {
        "activities": [
            {
                "name": "WaitActivity",
                "type": "Wait",
                "dependsOn": [],
                "typeProperties": {"waitTimeInSeconds": 15},
            }
        ]
    }
}
current_definition = operator.data_pipelines.get_definition(id=pipeline_id)
parts = current_definition["definition"]["parts"]
pipeline_content = json.dumps(update_def_payload)
pipeline_part = next((p for p in parts if p["path"] == "pipeline-content.json"), None)
if pipeline_part:
    pipeline_part["payload"] = encode_base64(pipeline_content)
else:
    parts.append({"path": "pipeline-content.json", "payload": encode_base64(pipeline_content)})
operator.data_pipelines.update_definition(id=pipeline_id, payload=current_definition)
print("Updated pipeline definition")
```

**Deleting a Data Pipeline**

```python
# Delete the pipeline
operator.data_pipelines.delete(id=pipeline_id)
print("Deleted pipeline")
```

#### Asynchronous Operations

**Creating a Data Pipeline Asynchronously**

```python
import asyncio
from fabrest.operator.workspace import WorkspaceOperator
from azure.identity import ClientSecretCredential

async def create_pipeline():
    # Initialize credentials and operator
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # Create a data pipeline asynchronously
    pipeline_name = "test_pipeline_async"
    response = await operator.data_pipelines.async_create(payload={"displayName": pipeline_name})
    pipeline_data = await response.json()
    pipeline_id = pipeline_data["id"]
    print(f"Created pipeline with ID: {pipeline_id}")
    return pipeline_id

# Run the async function
pipeline_id = asyncio.run(create_pipeline())
```

**Listing Data Pipelines Asynchronously**

```python
async def list_pipelines():
    # Initialize credentials and operator as above
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # List all data pipelines asynchronously
    pipelines = await operator.data_pipelines.async_list()
    for pipeline in pipelines:
        print(f"Pipeline: {pipeline['displayName']} (ID: {pipeline['id']})")

# Run the async function
asyncio.run(list_pipelines())
```

**Getting a Specific Data Pipeline Asynchronously**

```python
async def get_pipeline(pipeline_id):
    # Initialize credentials and operator as above
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # Get details of a specific pipeline asynchronously
    pipeline_data = await operator.data_pipelines.async_get(id=pipeline_id)
    print(f"Retrieved pipeline: {pipeline_data['displayName']} (ID: {pipeline_data['id']})")

# Run the async function
asyncio.run(get_pipeline(pipeline_id))
```

**Updating a Data Pipeline Name Asynchronously**

```python
async def update_pipeline_name(pipeline_id):
    # Initialize credentials and operator as above
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # Update pipeline name asynchronously
    updated_name = "test_pipeline_async_updated"
    await operator.data_pipelines.async_update(id=pipeline_id, payload={"displayName": updated_name})
    updated_data = await operator.data_pipelines.async_get(id=pipeline_id)
    print(f"Updated pipeline name to: {updated_data['displayName']}")

# Run the async function
asyncio.run(update_pipeline_name(pipeline_id))
```

**Updating a Data Pipeline Definition Asynchronously**

```python
import json
from fabrest.utils.functions import encode_base64

async def update_pipeline_definition(pipeline_id):
    # Initialize credentials and operator as above
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # Update pipeline definition asynchronously
    update_def_payload = {
        "properties": {
            "activities": [
                {
                    "name": "AsyncWaitActivity",
                    "type": "Wait",
                    "dependsOn": [],
                    "typeProperties": {"waitTimeInSeconds": 20},
                }
            ]
        }
    }
    current_definition = await operator.data_pipelines.async_get_definition(id=pipeline_id)
    parts = current_definition["definition"]["parts"]
    pipeline_content = json.dumps(update_def_payload)
    pipeline_part = next((p for p in parts if p["path"] == "pipeline-content.json"), None)
    if pipeline_part:
        pipeline_part["payload"] = encode_base64(pipeline_content)
    else:
        parts.append({"path": "pipeline-content.json", "payload": encode_base64(pipeline_content)})
    await operator.data_pipelines.async_update_definition(id=pipeline_id, payload=current_definition)
    print("Updated pipeline definition asynchronously")

# Run the async function
asyncio.run(update_pipeline_definition(pipeline_id))
```

**Deleting a Data Pipeline Asynchronously**

```python
async def delete_pipeline(pipeline_id):
    # Initialize credentials and operator as above
    credential = ClientSecretCredential(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id",
    )
    operator = WorkspaceOperator(id="your-workspace-id", credential=credential)

    # Delete the pipeline asynchronously
    await operator.data_pipelines.async_delete(id=pipeline_id)
    print("Deleted pipeline asynchronously")

# Run the async function
asyncio.run(delete_pipeline(pipeline_id))
```

For more detailed examples and API documentation, please refer to the [documentation](#documentation).

## Documentation

Detailed documentation is under development. For now, refer to the source code and inline comments for understanding the usage of different modules and functions.

## Contributing

Contributions to FabRest are welcome! Please feel free to submit a Pull Request or open an Issue on our GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any queries or support, please open an issue on the GitHub repository or contact the maintainers directly.

---

*Note: This project is not officially affiliated with Microsoft or the Fabric team. It is a community-driven effort to facilitate interaction with Fabric REST APIs.*