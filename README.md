# 📊 Data Engineering Job Tracker

This project is a small ETL pipeline for tracking software engineering job opportunities. It pulls job listings from the Adzuna API, cleans the raw payload, and stores the results in a local SQLite database.

The project is orchestrated with Apache Airflow running locally via Docker.

## 1. Problem Statement & Motivation

Job hunting as a software engineer is overwhelming. Roles open and close quickly across multiple platforms, making it hard to keep track of deadlines, salary data, and application links. This project automates the collection and storage of relevant jobs in one place so they can be reviewed and tracked over time.

## 2. Architecture Overview

The project is split into two layers:

- ETL logic: the Python functions that extract, transform, and load job data
- Orchestration: Apache Airflow, which schedules and runs those steps in order

```
[ EXTRACT ] -> fetch raw job data from Adzuna
      |
[ TRANSFORM ] -> clean titles, company names, locations, and salary values
      |
[ LOAD ] -> insert cleaned records into SQLite
```

## 3. Project Structure

```text
.
├── .env
├── .gitignore
├── README.md
├── docker-compose.yaml
├── dags/
│   ├── data_pipeline.py
│   └── job_tracker_dag.py
├── logs/
├── plugins/
├── config/
└── job_tracker.db
```

## 4. Local Setup

### Prerequisites

- Docker Desktop installed and running
- Git
- Python 3.x
- An Adzuna account with a valid app ID and app key

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd data-engineering-job-tracker
```

### 2. Create the environment file

Create a `.env` file in the project root with:

```env
AIRFLOW_UID=50000
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

### 3. Download the official Airflow Compose file

```bash
curl -LfO "https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml"
```

### 4. Pass Adzuna credentials to the Airflow containers

In the official `docker-compose.yaml`, add the following under the shared Airflow environment block:

```yaml
ADZUNA_APP_ID: ${ADZUNA_APP_ID}
ADZUNA_APP_KEY: ${ADZUNA_APP_KEY}
```

This makes sure the ETL code can access the credentials while it runs inside the container.

### 5. Create the required Airflow folders

```bash
mkdir -p dags logs plugins config
```

### 6. Start Airflow

```bash
docker compose up -d
```

Then check that the services are running:

```bash
docker compose ps
```

### 7. Open the Airflow UI

Visit:

```text
http://localhost:8080
```

Log in with:

- Username: `airflow`
- Password: `airflow`

## 5. Running the ETL Pipeline

Once Airflow is running, the DAG named `job_tracker_etl` will appear in the UI.

Trigger it manually from the Airflow dashboard.

The DAG executes the following tasks in order:

1. `extract_job_data`
2. `transform_job_data`
3. `load_job_data`

The ETL flow is:

- fetch raw job results from Adzuna
- clean the records into a consistent schema
- insert the cleaned records into SQLite

## 6. Database Schema

The pipeline writes to a SQLite database named `job_tracker.db`.

The `jobs` table includes:

- `id`
- `title`
- `company`
- `location`
- `salary`
- `url`
- `created_at`

## 7. Notes

- The ETL logic is intentionally kept separate from the orchestration layer.
- Airflow is only responsible for scheduling and running the pipeline.
- Local runtime folders such as `logs` and generated database files should not be committed to Git.
- Keep API credentials in `.env` and never commit secrets to source control.

## 8. Personal Reflection

This project taught me how important it is to separate data engineering logic from orchestration logic. The ETL pipeline itself was relatively straightforward, but running it inside Airflow introduced a new set of challenges around environment configuration, runtime dependencies, and making sure credentials were available inside the container.

I also learned that a pipeline is only as reliable as the environment it runs in. Locally, the script worked because the environment variables and Python setup were already in place. In Docker, I had to explicitly pass the Adzuna credentials into the Airflow services and understand how Airflow discovers DAGs and runs tasks in isolation. That made the project feel much more like a real production workflow.

Most importantly, I learned that small incremental changes matter. Fixing one issue at a time — first the ETL logic, then the Airflow wiring, and then the Docker environment — made the project much easier to reason about and track in Git. It also reinforced that data engineering is not just about writing transformations; it is about making those transformations dependable in a scheduled environment.