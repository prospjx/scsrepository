from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Student
from src.schemas import StudentProfile

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/{student_id}", response_model=StudentProfile)
def get_student(student_id: str, db: Session = Depends(get_db)):
    """Retrieves the profile and scheduling preferences for a student."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentProfile)
def update_student(
    student_id: str, profile_update: StudentProfile, db: Session = Depends(get_db)
):
    """Updates a student's preferences regarding workload, times, and difficulty."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = profile_update.name
    # Pydantic model is converted to dict for the JSON column
    student.preferences = profile_update.preferences.model_dump()

    db.commit()
    db.refresh(student)

    return student
