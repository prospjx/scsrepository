import os

# Set DATABASE_URL to SQLite before importing src modules to avoid trying to connect to Postgres
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src.models import Student
from src.seed import DEFAULT_STUDENT_ID

# In-memory SQLite database isolated per test session/run
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh database schema before each test and drop it afterwards."""
    from src import database, main

    Base.metadata.create_all(bind=engine)
    orig_sessionlocal_db = database.SessionLocal
    orig_sessionlocal_main = main.SessionLocal
    database.SessionLocal = TestingSessionLocal
    main.SessionLocal = TestingSessionLocal
    yield
    Base.metadata.drop_all(bind=engine)
    database.SessionLocal = orig_sessionlocal_db
    main.SessionLocal = orig_sessionlocal_main


@pytest.fixture
def db_session():
    """Yield a database session connected to the test database."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_student(db_session):
    """Seed a sample student in the test database or return the existing one seeded by lifespan."""
    student = (
        db_session.query(Student)
        .filter(Student.student_id == DEFAULT_STUDENT_ID)
        .first()
    )
    if student:
        student.name = "Jane Doe"
        student.preferences = {
            "max_credits_per_term": 16,
            "preferred_days_off": ["Monday", "Friday"],
            "difficulty_tolerance": "high",
            "preferred_time_of_day": "morning",
            "wake_up_time": "06:30",
            "sleep_time": "22:30",
            "study_hours_per_day": 4,
            "transit_time_minutes": 30,
            "gym_time_preference": "evening",
            "gym_duration_minutes": 45,
        }
    else:
        student = Student(
            student_id=DEFAULT_STUDENT_ID,
            name="Jane Doe",
            preferences={
                "max_credits_per_term": 16,
                "preferred_days_off": ["Monday", "Friday"],
                "difficulty_tolerance": "high",
                "preferred_time_of_day": "morning",
                "wake_up_time": "06:30",
                "sleep_time": "22:30",
                "study_hours_per_day": 4,
                "transit_time_minutes": 30,
                "gym_time_preference": "evening",
                "gym_duration_minutes": 45,
            },
        )
        db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student
