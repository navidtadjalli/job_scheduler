# Job Scheduler Service


> *This was implemented as part of a take-home interview assignment to build a reliable task scheduler service using FastAPI, Redis, and PostgreSQL with full test coverage.*


A minimal, scalable task scheduling service — inspired by cron — built using FastAPI, PostgreSQL, Redis, and APScheduler. This backend service allows tasks to be scheduled at specific times, executed reliably, and queried or managed via HTTP APIs.

---

## 🚀 Features

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
  "run_at": "2025-07-01T10:00:00Z"
}
```

---

### `GET /tasks`

List all tasks.

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

- `test_post_task.py`: Create task logic
  - Tests if the endpoint successfully creates a task
  - Tests if the endpoint handles exceptions during task creation

- `test_get_tasks.py`: Task listing
  - Tests if the endpoint returns the list of all tasks

- `test_delete_task.py`: Deletion + error handling
  - Tests if the endpoint checks for task existence
  - Tests if the task is properly deleted from the database
  - Tests if the endpoint handles scheduler failures and rolls back database changes when necessary

- `test_core_tasks.py`: `run_task()` logic and Redis locking
  - Tests if the function validates task existence
  - Tests if the task is executed and status updated to `Done` along with its result
  - Tests if Redis locking prevents double execution of the same task
  - Tests if the function handles exceptions during execution and updates the status to `Failed`
  - Tests if the task is only executed when its status is `Scheduled`

- `test_recovery.py`: Recovery behavior
  - Tests if the `fail` policy marks past-due tasks as `Failed`
  - Tests if the `skip` policy leaves past-due tasks unchanged
  - Tests if the `run` policy re-schedules past-due tasks
  - Tests if recovery handles scheduler failures gracefully
  - Tests if recovery works correctly when there are no tasks to process

- `test_lifespan.py`: Startup task restoration
  - Tests if FastAPI runs the lifespan logic and triggers task recovery on app startup


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
job_scheduler/config.py             11      0   100%
job_scheduler/constants.py           9      0   100%
job_scheduler/core/__init__.py       0      0   100%
job_scheduler/core/api.py           46      0   100%
job_scheduler/core/models.py        16      0   100%
job_scheduler/core/recovery.py      36      0   100%
job_scheduler/core/schemas.py       14      0   100%
job_scheduler/core/tasks.py         63      6    90%   56-57, 79-80, 98-99
job_scheduler/database.py            5      0   100%
job_scheduler/dependencies.py        6      0   100%
job_scheduler/exceptions.py         19      0   100%
job_scheduler/logger.py             10      1    90%   19
job_scheduler/main.py               16      4    75%   14-17
job_scheduler/redis_client.py        3      0   100%
--------------------------------------------------------------
TOTAL                              254     11    96%
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
│   └── test_lifespan.py            # Lifespan startup behavior
│
├── .env.sample                     # Sample env vars for local dev
├── .gitignore                      # Git exclusions (e.g., venv, pycache)
├── migrate.py                      # Schema initializer using SQLAlchemy
├── pyproject.toml                  # Project metadata + pytest plugins
├── pytest.ini                      # Pytest config and options
└── requirements.txt                # Python dependencies list
```
