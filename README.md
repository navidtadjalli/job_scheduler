# Job Scheduler Service


> *This was implemented as part of a take-home interview assignment to build a reliable task scheduler service using FastAPI, Redis, and PostgreSQL with full test coverage.*


A minimal, scalable task scheduling service — inspired by cron — built using FastAPI, PostgreSQL, Redis, and APScheduler. This backend service allows tasks to be scheduled at specific times, executed reliably, and queried or managed via HTTP APIs.

---

## 🚀 Features

- Support for recurring tasks via `cron`, `interval_seconds`, or `run_at` expression
- Schedule tasks to run at a specific time (`POST /tasks`)
- Automatically execute tasks and store results (`APScheduler`)
- View all scheduled and completed tasks (`GET /tasks`)
- Remove scheduled tasks (`DELETE /tasks/{id}`)
- Automatically recover unsent tasks after restarts (via `lifespan`)
- Redis-based locking to prevent double execution
- Configurable recovery policy via `.env`
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

### 📦 Dockerized Setup (optional)

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
  "name": "send_report",
  "cron": "0 9 * * *",
  "interval_seconds": 3600,
  "run_at": "2025-07-01T10:00:00Z"
}
```

#### Task Timing Options

You can specify **when** the task should run using one of the following:

| Field              | Type     | Meaning                              |
| ------------------ | -------- | ------------------------------------ |
| `cron`             | string   | Cron expression (e.g. `"0 9 * * *"`) |
| `interval_seconds` | integer  | Run every N seconds                  |
| `run_at`           | datetime | One-time scheduled time              |

> **Priority rule**
>
> If multiple fields are provided, only one will be used — in this order of precedence:  
>
> ```text
> cron → interval_seconds → run_at
> ```

#### Validations

* At least **one** of `cron`, `interval_seconds`, or `run_at` **must** be provided
* `interval_seconds` must be a positive integer if provided
* `cron` must be a valid crontab expression (format like `"*/5 * * * *"`)

---
### `GET /tasks`

Returns a list of all scheduled or completed tasks.

#### Response format:

```json
[
  {
    "task_id": "8f89113e-389a-4d10-8fd2-2f2a24088ac2",
    "name": "send_report",
    "run_at": "2025-07-01T10:00:00Z",
    "status": "done",
    "result": "Task completed successfully",
    "created_at": "2025-06-30T15:45:21.123456"
  }
]
```

> **Note:**
> If a task was created using `cron` or `interval_seconds`, those fields are **not shown** in the response. Only `run_at` is returned as the "next execution time" for compatibility.

### 🔍 `TaskRead` Schema Fields:

| Field        | Type        | Description                          |
| ------------ | ----------- | ------------------------------------ |
| `task_id`    | string      | Unique ID of the task                |
| `name`       | string      | Name or label for the task           |
| `run_at`     | datetime    | Scheduled execution time (next run)  |
| `status`     | enum        | `scheduled`, `done`, or `failed`     |
| `result`     | string/null | Output or log result (once run)      |
| `created_at` | datetime    | When the task was originally created |

---

### `DELETE /tasks/{task_id}`

Cancel a scheduled task (if not yet executed).

---

## ⚙️ Configuration (`.env`)

| Variable              | Description                                 | Example                                                       |
|-----------------------|---------------------------------------------|---------------------------------------------------------------|
| `RECOVER_PAST_TASKS`  | What to do with tasks whose run time passed | `skip` / `fail` / `run`                                       |
| `REDIS_URL`           | Redis connection string                     | `redis://localhost:6379/0`                                    |
| `DB_URL`              | SQLAlchemy DB URI                           | `postgresql+psycopg2://postgres:postgres@db:5432/schedule_db` |

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
  - Tests if the task is executed and status updated to `Done` along with its result
  - Tests if Redis locking prevents double execution of the same task
  - Tests if the function handles exceptions during execution and updates the status to `Failed`
  - Tests if the task is only executed when its status is `Scheduled`
  - Tests if the task is executed with `cron` property being set
  - Tests if the task is executed with `interval_seconds` property being set
  - Tests if the task is executed with `run_at` property being set
  - Tests if the `scheduled_task` checks that at least one of `cron`, `interval_seconds`, or `run_at` is set and if not raised an exception

- `test_delete_task.py`: Deletion + error handling
  - Tests if the endpoint checks for task existence
  - Tests if the task is properly deleted from the database
  - Tests if the endpoint handles scheduler failures and rolls back database changes when necessary

- `test_get_tasks.py`: Task listing
  - Tests if the endpoint returns the list of all tasks

- `test_health_check.py`: `/health` endpoint
  - Tests if the endpoint works correctly

- `test_lifespan.py`: Startup task restoration
  - Tests if FastAPI runs the lifespan logic and triggers task recovery on app startup

- `test_post_task.py`: Create task logic
  - Tests if the endpoint successfully creates a task
  - Tests if the endpoint handles exceptions during task creation

- `test_recovery.py`: Recovery behavior
  - Tests if the `fail` policy marks past-due tasks as `Failed`
  - Tests if the `skip` policy leaves past-due tasks unchanged
  - Tests if the `run` policy re-schedules past-due tasks
  - Tests if recovery handles scheduler failures gracefully
  - Tests if recovery works correctly when there are no tasks to process

- `test_schemas.py`: Schema and validation logic
  - Tests if a task is valid with only a valid `cron`
  - Tests if a task is valid with only a valid `run_at`
  - Tests if a task is valid with only a valid `interval_seconds`
  - Tests if a task is valid when all three timing fields are present
  - Tests if a task is **invalid** when none of the timing fields are provided
  - Tests if a task is **invalid** when a negative value is passed for `interval_seconds`

---

### 📊 Coverage Report

To generate coverage:

```bash
pytest --cov=job_scheduler --cov-report=term-missing --cov-report=html
```

This will output:
- Terminal coverage % with uncovered lines
- HTML report at `htmlcov/index.html` (open in browser)

---
### ✅ Test Coverage

```bash
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
job_scheduler/__init__.py            0      0   100%
job_scheduler/config.py             17      0   100%
job_scheduler/constants.py          12      0   100%
job_scheduler/core/__init__.py       0      0   100%
job_scheduler/core/api.py           46      0   100%
job_scheduler/core/models.py        16      0   100%
job_scheduler/core/recovery.py      36      0   100%
job_scheduler/core/schemas.py       27      0   100%
job_scheduler/core/tasks.py         73      4    95%   62-63, 85-86
job_scheduler/database.py           14      4    71%   11-14
job_scheduler/dependencies.py        6      0   100%
job_scheduler/exceptions.py         19      0   100%
job_scheduler/logger.py             10      1    90%   19
job_scheduler/main.py               19      4    79%   14-17
job_scheduler/redis_client.py        3      0   100%
--------------------------------------------------------------
TOTAL                              298     13    96%
```

---

## 🧠 Design Justification

This service uses **FastAPI** to provide a clean and testable interface for interacting with a lightweight job scheduler. PostgreSQL was selected to support concurrent writes, transactional safety, and containerized multi-node deployments. The schema remains flat, but can evolve into relational models (e.g., tasks linked to users or audit logs), while **Redis locks** guarantee safe execution even in a distributed setup. The design is modular, extensible, and robust against failure — with full test coverage and environment-based configuration.

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
│   ├── redis_client.py             # Redis connection + locking helper
│   └── core/                       # Core domain logic
│       ├── api.py                  # FastAPI route handlers
│       ├── models.py               # SQLAlchemy task models
│       ├── recovery.py             # Task recovery on app restart
│       ├── schemas.py              # Pydantic request/response models
│       └── tasks.py                # Task runner logic + Redis locking
│
├── tests/                          # Pytest-based test suite
│   ├── conftest.py                 # Shared fixtures (e.g., DB setup)
│   ├── test_post_task.py           # POST /tasks
│   ├── test_get_tasks.py           # GET /tasks
│   ├── test_delete_task.py         # DELETE /tasks/{id}
│   ├── test_core_tasks.py          # run_task function logic
│   ├── test_recovery.py            # Task recovery scenarios
│   ├── test_lifespan.py            # Lifespan startup behavior
│   └── test_schemas.py             # Tests for `TaskCreate` schema validation
│
├── .env.sample                     # Sample env vars for local dev
├── .gitignore                      # Git exclusions (e.g., venv, pycache)
├── migrate.py                      # Schema initializer using SQLAlchemy
├── pyproject.toml                  # Project metadata + pytest plugins
├── pytest.ini                      # Pytest config and options
└── requirements.txt                # Python dependencies list
```
