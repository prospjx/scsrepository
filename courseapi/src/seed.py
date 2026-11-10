from sqlalchemy.orm import Session

from src.models import Course, Timeslot


def seed_db(db: Session):
    # Check if we already have data
    if db.query(Course).first():
        return

    print("Seeding initial course data...")

    cs3410 = Course(
        course_id="CS-3410",
        title="Computer Systems",
        credits=4,
        description="Introduction to computer systems.",
        prerequisites=[],
    )

    cs3500 = Course(
        course_id="CS-3500",
        title="Software Engineering",
        credits=4,
        description="Software engineering principles.",
        prerequisites=["CS-3410"],
    )

    math2310 = Course(
        course_id="MATH-2310",
        title="Linear Algebra",
        credits=3,
        description="Matrices and vector spaces.",
        prerequisites=[],
    )

    db.add_all([cs3410, cs3500, math2310])
    db.commit()

    # Timeslots for the courses
    ts1 = Timeslot(
        course_id="CS-3410",
        day="Monday",
        start_time="10:00",
        end_time="11:15",
        location="Building A, Room 101",
    )
    ts2 = Timeslot(
        course_id="CS-3410",
        day="Wednesday",
        start_time="10:00",
        end_time="11:15",
        location="Building A, Room 101",
    )

    ts3 = Timeslot(
        course_id="CS-3500",
        day="Tuesday",
        start_time="13:00",
        end_time="14:15",
        location="Building C, Room 301",
    )
    ts4 = Timeslot(
        course_id="CS-3500",
        day="Thursday",
        start_time="13:00",
        end_time="14:15",
        location="Building C, Room 301",
    )

    ts5 = Timeslot(
        course_id="MATH-2310",
        day="Tuesday",
        start_time="09:00",
        end_time="10:15",
        location="Building B, Room 204",
    )
    ts6 = Timeslot(
        course_id="MATH-2310",
        day="Thursday",
        start_time="09:00",
        end_time="10:15",
        location="Building B, Room 204",
    )

    db.add_all([ts1, ts2, ts3, ts4, ts5, ts6])
    db.commit()
    print("Database seeding completed.")
