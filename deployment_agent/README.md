# Deployment Agent

A simple deployment agent that copies generated DAG files from the pipeline generator agent's output directory to the Airflow DAGs directory.

## Features

- **File Copying**: Copies generated DAG files from `pipeline_generator_agent/output/` to `airflow/dags/`
- **Batch Deployment**: Deploy all available DAG files at once
- **Individual Deployment**: Deploy specific DAG files
- **File Management**: Remove DAG files from Airflow directory
- **Status Monitoring**: Check deployment status and available files
- **REST API**: FastAPI-based web service for remote deployment
- **Error Handling**: Comprehensive error handling and logging

## Usage

### Command Line Usage

```python
from deployment_agent import DeploymentAgent

# Initialize the agent
agent = DeploymentAgent()

# List available DAG files
dags = agent.list_available_dags()
print(f"Available DAGs: {dags}")

# Deploy a specific DAG
success = agent.deploy_dag("my_dag.py")

# Deploy all available DAGs
results = agent.deploy_all_dags()

# Check deployment status
status = agent.get_deployment_status()
print(f"Deployed files: {status['deployed_files']}")

# Remove a DAG file
agent.remove_dag("old_dag.py")
```

### API Usage

Start the API server:
```bash
python app.py
```

The API will be available at `http://localhost:8003`

#### Available Endpoints

- `GET /` - API information and available endpoints
- `GET /status` - Get deployment status
- `GET /dags` - List available DAG files
- `POST /deploy` - Deploy a specific DAG file
- `POST /deploy-all` - Deploy all available DAG files
- `POST /remove` - Remove a DAG file
- `GET /health` - Health check

#### Example API Calls

```bash
# Get deployment status
curl http://localhost:8003/status

# List available DAGs
curl http://localhost:8003/dags

# Deploy a specific DAG
curl -X POST http://localhost:8003/deploy \
  -H "Content-Type: application/json" \
  -d '{"dag_filename": "my_dag.py", "overwrite": true}'

# Deploy all DAGs
curl -X POST http://localhost:8003/deploy-all \
  -H "Content-Type: application/json" \
  -d '{"overwrite": true}'

# Remove a DAG
curl -X POST http://localhost:8003/remove \
  -H "Content-Type: application/json" \
  -d '{"dag_filename": "old_dag.py"}'
```

## Configuration

The deployment agent uses the following default paths:

- **Source Directory**: `../pipeline_generator_agent/output/`
- **Target Directory**: `../airflow/dags/`

You can customize these paths when initializing the agent:

```python
agent = DeploymentAgent(
    source_dir="/path/to/source",
    target_dir="/path/to/target",
    project_root="/path/to/project"
)
```

## File Structure

```
deployment_agent/
├── deployment_agent.py    # Main DeploymentAgent class
├── app.py                # FastAPI web service
└── README.md             # This file
```

## Dependencies

- `fastapi` - Web framework for the API
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `pathlib` - Path handling (built-in)
- `shutil` - File operations (built-in)
- `logging` - Logging (built-in)

## Integration

This deployment agent is designed to work with the pipeline generator agent. When the pipeline generator creates a new DAG file in its output directory, the deployment agent can copy it to the Airflow DAGs directory for execution.

The typical workflow is:
1. Pipeline generator creates a DAG file in `pipeline_generator_agent/output/`
2. Deployment agent copies the file to `airflow/dags/`
3. Airflow picks up the new DAG and makes it available for execution
