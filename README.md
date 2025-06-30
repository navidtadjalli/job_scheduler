# Job Scheduler Service

A minimal, scalable task scheduling service — inspired by cron — built using FastAPI, SQLite, and APScheduler. This backend service allows tasks to be scheduled at specific times, executed reliably, and queried or managed via HTTP APIs.

---

## 🚀 Features

- Schedule tasks to run at a specific time (`POST /tasks`)
- Automatically execute tasks and store results (`APScheduler`)
- View all scheduled and completed tasks (`GET /tasks`)
- Remove scheduled tasks (`DELETE /tasks/{id}`)
- Automatically recover unsent tasks after restarts
- Redis-based locking to prevent double execution
- Configurable recovery policy via `.env`

---

## 📦 Tech Stack

- **FastAPI** — async web framework
- **SQLite** — embedded relational DB (simple + file-based)
- **APScheduler** — robust job scheduler
- **Redis** — distributed locking for task execution
- **Pydantic v2 + pydantic-settings** — clean config & validation
- **Pytest** — test suite with full coverage

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

---

## 🌐 API Endpoints

### `POST /tasks`

Schedule a new task.

```json
{
  "name": "send_report",
  "run_at": "2025-07-01T10:00:00"
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

| Variable              | Description                                 | Example                      |
|-----------------------|---------------------------------------------|------------------------------|
| `RECOVER_PAST_TASKS`  | What to do with tasks whose run time passed | `skip` / `fail` / `run`      |
| `REDIS_URL`           | Redis connection string                     | `redis://localhost:6379/0`   |
| `DB_URL`              | SQLAlchemy DB URI                           | `sqlite:///./tasks.db`       |

📁 See `.env.sample` for a template.

---

## 🧪 Testing

```bash
pytest
```

Includes:
- Unit tests for all endpoints
- Full recovery behavior under all `RECOVER_PAST_TASKS` modes
- Scheduler error cases

---

## 🧠 Design Justification

This service uses **FastAPI** to provide a clean and testable interface for interacting with a lightweight job scheduler. SQLite was chosen for simplicity and persistence, while **Redis locks** guarantee safe execution even in a distributed setup. The design is modular, extensible, and robust against failure — with full test coverage and environment-based configuration.

---

## 📂 Folder Structure

```
job_scheduler/
├── job_scheduler/        # Core application logic
│   ├── main.py           # Entry point with FastAPI + scheduler
│   ├── config.py         # App settings (env-based)
│   ├── core/             # Domain logic
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── tasks.py      # Scheduling logic
│   │   ├── recovery.py   # Restart-safe logic
│   │   └── api.py        # HTTP routes
├── tests/                # Pytest-based test suite
├── migrate.py            # DB schema initializer
├── .env.sample           # Example configuration
```

---

## ✅ Author & Notes

This project was created as part of a technical interview task to design a minimal task scheduling service. It follows best practices in service design, testability, and modularity.