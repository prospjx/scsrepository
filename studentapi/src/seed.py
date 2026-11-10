from sqlalchemy.orm import Session

from src.models import Student

# We use a static mock ID so you can reliably copy/paste it while testing the Scheduler API
DEFAULT_STUDENT_ID = "123e4567-e89b-12d3-a456-426614174000"


def seed_db(db: Session):
    if db.query(Student).first():
        return

    print("Seeding initial student profile...")

    mock_student = Student(
        student_id=DEFAULT_STUDENT_ID,
        name="John Doe",
        preferences={
            "max_credits_per_term": 18,
            "preferred_days_off": ["Friday"],
            "difficulty_tolerance": "medium",
            "preferred_time_of_day": "morning",
            "wake_up_time": "07:00",
            "sleep_time": "23:00",
            "study_hours_per_day": 3,
            "transit_time_minutes": 45,
            "gym_time_preference": "afternoon",
            "gym_duration_minutes": 60,
            "energy_chronotype": "morning_lark",
            "study_session_style": "deep_work",
            "min_gap_for_commute_hours": 3,
        },
    )

    db.add(mock_student)
    db.commit()
    print(f"Mock student created with ID: {DEFAULT_STUDENT_ID}")
