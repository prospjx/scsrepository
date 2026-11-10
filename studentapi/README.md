# Student Profiles & Preferences Microservice (`studentapi`)

A microservice built with **FastAPI** and **PostgreSQL** that manages student academic records and comprehensive personal life preferences (commute time, wake/sleep schedules, workout preferences, and study allocations).

---

## Features

- **Student Academic Profiles**: Manages student identity, degree programs, completed courses, and enrolled term credits.
- **Life Routine Preferences**:
  - `wake_up_time`: Preferred wake-up target (e.g. `07:00`).
  - `sleep_time`: Bedtime target (e.g. `23:00`).
  - `transit_time_minutes`: Estimated one-way commute duration to campus.
  - `study_hours_per_day`: Daily target study volume.
  - `gym_time_preference`: Preferred workout window (`morning`, `afternoon`, `evening`).
  - `gym_duration_minutes`: Workout duration in minutes.
- **Relational Storage**: Backed by PostgreSQL (`students_db`) with SQLAlchemy and Alembic migrations.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/students/{student_id}` | Retrieve full student profile and preferences. |
| `POST` | `/api/v1/students` | Register a new student profile. |
| `PUT` | `/api/v1/students/{student_id}` | Update student profile and routine preferences. |
| `DELETE` | `/api/v1/students/{student_id}` | Remove a student profile. |
| `GET` | `/health` | Service health check probe. |

---

## Configuration & Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@localhost:5432/students_db` | PostgreSQL database connection string. |
| `PORT` | `8002` | HTTP listen port. |
| `HOST` | `0.0.0.0` | Host bind address. |

---

## Local Development

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start service
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

### Running Tests
```bash
pytest tests/ -v
```

---

## Deployment

Packaged as a Helm chart inside `gitops/charts/studentapi`:
```bash
docker build -t ghcr.io/prospjx/student-api:latest .
helm upgrade --install studentapi ../gitops/charts/studentapi
```
