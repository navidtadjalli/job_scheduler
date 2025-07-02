# Job Scheduler Service


> *This was implemented as part of a take-home interview assignment to build a reliable task scheduler service using FastAPI, Redis, and PostgreSQL with full test coverage.*


A minimal, scalable task scheduling service — inspired by cron — built using FastAPI, PostgreSQL, Redis, and APScheduler. This backend service allows tasks to be scheduled at specific times like `crontab`, executed reliably, and queried or managed via HTTP APIs.

---

## 🚀 Features

- Support for recurring tasks via `cron`
- Schedule tasks to run at a specific time (`POST /tasks`)
- Automatically execute tasks and store results (`APScheduler`)
- View all scheduled and completed tasks (`GET /tasks`)
- Remove scheduled tasks (`DELETE /tasks/{slug}`)
- Automatically recover unsent tasks after restarts (via `lifespan`)
- Redis-based locking to prevent double execution
- **Full test coverage including exception paths and startup logic**

---

## 📦 Tech Stack

- **FastAPI** — async web framework
- **PostgreSQL** — production-grade relational database with concurrency and transaction support
- **APScheduler** — robust job scheduler
- **Redis** — distributed locking for task execution
- **Pydantic v2 + pydantic-settings** — clean config & validation
- **Pytest** — test suite with full coverage
- **Lifespan API** — used for startup recovery hook
- **pytest-cov** — test coverage measurement

---

## 🧠 Design Justification

This service uses **FastAPI** to provide a clean and testable interface for interacting with a lightweight job scheduler. PostgreSQL was selected to support concurrent writes, transactional safety, and containerized multi-node deployments. The schema remains flat, but can evolve into relational models (e.g., tasks linked to users), while **Redis locks** guarantee safe execution even in a distributed setup. The design is modular, extensible, and robust against failure — with full test coverage and environment-based configuration.

---

## 🛠️ Setup & Run

### 📁 Install dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ Create DB schema

```bash
python migrate.py
```

### ▶️ Run the app

```bash
uvicorn job_scheduler.main:app --reload
```

### 📦 Dockerized Setup

You can also use Docker Compose to spin up everything:

```bash
docker-compose up --build
```

This will start:

* FastAPI app
* PostgreSQL (`db`)
* Redis (`redis`)

---

## 🌐 API Endpoints

### `POST /tasks`

Schedule a new task.

```json
{
  "name": "task name",
  "cron_expression": "3 */3 * * *"
}
```

#### Validations

* `cron` must be a valid crontab expression (format like `"*/5 * * * *"`)

---
### `GET /tasks`

Returns a paginated list of scheduled tasks.

#### Query Parameters:

| Parameter | Type | Default | Description                              |
|-----------|------|---------|------------------------------------------|
| `offset`  | int  | 0       | Number of records to skip                |
| `limit`   | int  | 10      | Max number of tasks to return (max: 100) |

Example:
```bash
GET /tasks?offset=0&limit=10
```

#### Response format:

```json
{
  "count": 1,
  "result": [
    {
      "slug": "0kK5OrHMBp",
      "name": "task name",
      "cron_expression": "3 */3 * * *",
      "created_at": "2025-07-02T02:27:29.765354",
      "next_run_at": "2025-07-02T02:30:00"
    }
  ]
}
```

---
### `DELETE /tasks/{slug}`

Cancel a scheduled task (if not yet executed).

---
### `GET /tasks/{slug}/results`

Returns a paginated list of execution results for a specific scheduled task.

#### Path Parameters:

| Parameter   | Type    | Description                   |
|-------------|---------|-------------------------------|
| `task_slug` | string  | The slug identifier of a task |


Parameter	Type	Description
task_slug	string	

#### Query Parameters:

| Parameter | Type | Default | Description                              |
|-----------|------|---------|------------------------------------------|
| `offset`  | int  | 0       | Number of records to skip                |
| `limit`   | int  | 10      | Max number of tasks to return (max: 100) |

Example:
```bash
GET /tasks/demo-slug/results?offset=0&limit=10
```

#### Response format:

```json
{
  "count": 1,
  "result": [
    {
      "executed_at": "2025-07-02T03:38:45.210Z",
      "status": "Done",
      "result": "string"
    }
  ]
}
```
---

## ⚙️ Configuration (`.env`)

| Variable              | Description                                 | Example                                                       |
|-----------------------|---------------------------------------------|---------------------------------------------------------------|
| `REDIS_URL`           | Redis connection string                     | `redis://localhost:6379/0`                                    |
| `DB_URL`              | SQLAlchemy DB URI                           | `postgresql+psycopg2://postgres:postgres@db:5432/schedule_db` |
| `PHASE`               | Current Environment                         | `local`                                                       |

📁 See `.env.sample` for a template.

---

## 🧪 Testing

```bash
pytest
```

### ✅ Test Modules and Their Scenarios

- `test_config.py`: Settings of Project
  - Tests if Settings class checks `DB_URL` is set
  - Tests if Settings class checks `REDIS_URL` is set

- `test_core_tasks.py`: `run_task()` logic and Redis locking
  - Tests if the function validates task existence
  - Tests if the `get_result` function works
  - Tests if the `get_result_for_error` function works
  - Tests if the task gets execute and its `next_run_at` gets updated and `ExecutedTask` is added with `ResultStatus.Done` status
  - Tests if Redis locking prevents double execution of the same task
  - Tests if the function handles exceptions during execution and the task's `next_run_at` gets updated and `ExecutedTask` is added with `ResultStatus.Done` status
  - Tests if the task's trigger is `CronTrigger`

- `test_delete_task.py`: Deletion + error handling
  - Tests if the endpoint checks for task existence
  - Tests if the task is properly deleted from the database
  - Tests if the endpoint handles scheduler failures and rolls back database changes when necessary

- `test_get_task_results.py`: Task's results listing
  - Tests if the endpoint checks task's existence
  - Tests if the endpoint returns the list of all task's results in paginated format
  - Tests if the endpoint pagination parameters (`offset`, `limit`) works and the result is sorted by `executed_at`

- `test_get_tasks.py`: Task listing
  - Tests if the endpoint returns the list of all tasks in paginated format
  - Tests if the endpoint pagination parameters (`offset`, `limit`) works and the result is sorted by `created_at`

- `test_health_check.py`: `/health` endpoint
  - Tests if the endpoint works correctly

- `test_lifespan.py`: Startup task restoration
  - Tests if FastAPI runs the lifespan logic and triggers task recovery on app startup

- `test_post_task.py`: Create task logic
  - Tests if the endpoint successfully creates a task with `cron_expression` value being set
  - Tests if `next_run_at` is getting set and its value is calculated correctly
  - Tests if the endpoint handles exceptions during task creation

- `test_recovery.py`: Recovery behavior
  - Tests if recovery works and reschedule all the added tasks
  - Tests if recovery handles scheduler failures gracefully
  - Tests if recovery works correctly when there are no tasks to process

- `test_schemas.py`: Schema and validation logic
  - Tests if a task is valid with a valid `cron_expression`
  - Tests if schema validates the value of `cron_expression` field
  - Tests if a task is **invalid** when `cron_expression` field is missing

---

### 📊 Coverage Report

To generate coverage:

```bash
pytest --cov=job_scheduler --cov=core --cov-report=term-missing --cov-report=html
```

This will output:
- Terminal coverage % with uncovered lines
- HTML report at `htmlcov/index.html` (open in browser)

---
### ✅ Test Coverage

```bash
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
core/__init__.py                    0      0   100%
core/api.py                        15      0   100%
core/models.py                     26      0   100%
core/recovery.py                   17      0   100%
core/schemas.py                    35      1    97%   16
core/services.py                   42      0   100%
core/tasks.py                      76      4    95%   51-52, 100-101
job_scheduler/__init__.py           0      0   100%
job_scheduler/config.py            16      0   100%
job_scheduler/constants.py          7      0   100%
job_scheduler/database.py          14      4    71%   11-14
job_scheduler/dependencies.py       6      0   100%
job_scheduler/exceptions.py        19      0   100%
job_scheduler/logger.py             9      1    89%   17
job_scheduler/main.py              19      4    79%   14-17
job_scheduler/redis_client.py       3      0   100%
-------------------------------------------------------------
TOTAL                             304     14    95%
```

---

## 📂 Folder Structure

```
job_scheduler/
├── job_scheduler/                  # Core application package
│   ├── main.py                     # FastAPI app entry point + lifespan
│   ├── config.py                   # Environment-based settings via Pydantic
│   ├── constants.py                # Centralized constants and identifiers
│   ├── database.py                 # SQLAlchemy engine and session factory
│   ├── dependencies.py             # FastAPI dependencies (e.g., DB access)
│   ├── exceptions.py               # Custom exceptions with error codes
│   ├── logger.py                   # App-wide logging configuration
│   └── redis_client.py             # Redis connection + locking helper
│
├── core/                           # Core domain logic
│   ├── api.py                      # FastAPI route handlers
│   ├── models.py                   # SQLAlchemy task models
│   ├── recovery.py                 # Task recovery on app restart
│   ├── schemas.py                  # Pydantic request/response models
│   ├── services.py                 # Logic of endpoints
│   └── tasks.py                    # Task runner logic + Redis locking
│
├── tests/                          # Pytest-based test suite
│   ├── conftest.py                 # Shared fixtures (e.g., DB setup)
│   ├── test_config.py              # Config
│   ├── test_core_tasks.py          # run_task function logic
│   ├── test_delete_task.py         # DELETE /tasks/{slug}
│   ├── test_get_task_results.py    # GET /tasks/{slug}/results
│   ├── test_get_tasks.py           # GET /tasks
│   ├── test_health_check.py        # GET /health
│   ├── test_lifespan.py            # Lifespan startup behavior
│   ├── test_post_task.py           # POST /tasks
│   ├── test_recovery.py            # Task recovery scenarios
│   └── test_schemas.py             # Tests for `TaskCreate` schema validation
│
├── .env.sample                     # Sample env vars for local dev
├── .gitignore                      # Git exclusions (e.g., venv, pycache)
├── Dockerfile                      # FastAPI app container build config  
├── docker-compose.yml              # App + PostgreSQL + Redis orchestration
├── migrate.py                      # Schema initializer using SQLAlchemy
├── pyproject.toml                  # Project metadata + pytest plugins
└── requirements.txt                # Python dependencies list
```
