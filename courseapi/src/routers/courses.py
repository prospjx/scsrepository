from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Course
from src.schemas import CourseResponse

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """Retrieves a list of all courses available in the catalog."""
    return db.query(Course).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course_details(course_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific course."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=CourseResponse)
def create_or_update_course(course_data: CourseResponse, db: Session = Depends(get_db)):
    """Registers or updates a course and its timeslots in the catalog."""
    from src.models import Timeslot

    existing = (
        db.query(Course).filter(Course.course_id == course_data.course_id).first()
    )
    if existing:
        existing.title = course_data.title
        existing.credits = course_data.credits
        existing.description = course_data.description
        existing.prerequisites = course_data.prerequisites
        db.query(Timeslot).filter(Timeslot.course_id == course_data.course_id).delete()
        for ts in course_data.timeslots:
            db.add(
                Timeslot(
                    course_id=course_data.course_id,
                    day=ts.day,
                    start_time=ts.start_time,
                    end_time=ts.end_time,
                    location=ts.location,
                )
            )
        db.commit()
        db.refresh(existing)
        return existing

    new_course = Course(
        course_id=course_data.course_id,
        title=course_data.title,
        credits=course_data.credits,
        description=course_data.description,
        prerequisites=course_data.prerequisites,
    )
    db.add(new_course)
    db.flush()
    for ts in course_data.timeslots:
        db.add(
            Timeslot(
                course_id=new_course.course_id,
                day=ts.day,
                start_time=ts.start_time,
                end_time=ts.end_time,
                location=ts.location,
            )
        )
    db.commit()
    db.refresh(new_course)
    return new_course
