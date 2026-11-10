# Course Catalog Microservice (`courseapi`)

A microservice built with **FastAPI** and **PostgreSQL** that manages the university course catalog, lecture sections, time slots, prerequisites, and credit allocations.

---

## Features

- **Course Catalog Management**: CRUD operations for academic courses, department codes, and difficulty ratings.
- **Section & Time Slot Tracking**: Supports multi-day schedule meetings (e.g. Mon/Wed/Fri, Tue/Thu) with 24-hour time ranges and campus locations.
- **Prerequisite Validation**: Stores prerequisite requirements to prevent invalid schedule enrollments.
- **PostgreSQL Persistence**: Managed with SQLAlchemy ORM and structured Pydantic schemas.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/courses` | List all available courses in the catalog. |
| `GET` | `/api/v1/courses/{course_id}` | Retrieve details and timeslots for a specific course. |
| `POST` | `/api/v1/courses` | Create a new course entry. |
| `PUT` | `/api/v1/courses/{course_id}` | Update course metadata, credits, or schedule slots. |
| `DELETE` | `/api/v1/courses/{course_id}` | Remove a course from the catalog. |
| `GET` | `/health` | Kubernetes health probe. |

---

## Configuration & Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@localhost:5432/courses_db` | PostgreSQL connection string. |
| `PORT` | `8001` | Server port. |
| `HOST` | `0.0.0.0` | Host bind address. |

---

## Local Development

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations / start service
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Running Tests
```bash
pytest tests/ -v
```

---

## Deployment

Packaged as a Helm chart inside `gitops/charts/courseapi`:
```bash
docker build -t ghcr.io/prospjx/course-api:latest .
helm upgrade --install courseapi ../gitops/charts/courseapi
```
