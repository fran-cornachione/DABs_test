# my_dabs_project

Databricks Asset Bundle (DABs) project with CI/CD via GitHub Actions.

## Project Structure

```
.
├── databricks.yml                  # Bundle root config (targets: dev / staging / prod)
├── resources/
│   └── jobs.yml                    # Job & DLT pipeline definitions
├── src/
│   └── notebooks/
│       ├── 01_ingest_data.py       # Bronze layer ingestion
│       ├── 02_transform_data.py    # Silver layer transformation
│       ├── 03_load_data.py         # Gold layer aggregation
│       └── dlt_pipeline.py         # Delta Live Tables pipeline
├── tests/
│   └── test_transformations.py     # PySpark unit tests (no cluster needed)
├── requirements-dev.txt
└── .github/
    └── workflows/
        └── deploy.yml              # CI/CD pipeline
```

## Prerequisites

- Databricks CLI v0.200+ installed
- A Databricks workspace (Unity Catalog enabled recommended)
- GitHub repository with the secrets below

## GitHub Secrets Required

| Secret | Description |
|---|---|
| `DATABRICKS_HOST` | Workspace URL, e.g. `https://adb-123.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal Access Token or Service Principal token |

Set them in **Settings → Secrets and variables → Actions**.

## Branch → Environment Mapping

| Branch | Target | Notes |
|---|---|---|
| `develop` | `dev` | Auto-deploy after tests pass |
| `staging` | `staging` | Auto-deploy after tests pass |
| `main` | `prod` | Requires manual approval (GitHub Environment) |

## Local Development

```bash
# Install CLI
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Authenticate
databricks auth login --host https://<your-workspace>.azuredatabricks.net

# Validate
databricks bundle validate -t dev

# Deploy to dev
databricks bundle deploy -t dev

# Trigger a job manually
databricks bundle run etl_pipeline_job -t dev

# Destroy (cleanup)
databricks bundle destroy -t dev
```

## Running Tests Locally

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Adding a New Job

1. Add a new entry under `resources/jobs.yml` → `resources.jobs`
2. Add any new notebooks under `src/notebooks/`
3. Run `databricks bundle validate -t dev` to check the config
4. Push to `develop` — the pipeline does the rest
