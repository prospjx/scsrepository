from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

    # Store prerequisites as a simple JSON array
    prerequisites = Column(JSON, default=list)

    # Relationship to timeslots
    timeslots = relationship(
        "Timeslot", back_populates="course", cascade="all, delete-orphan"
    )


class Timeslot(Base):
    __tablename__ = "timeslots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(String, ForeignKey("courses.course_id"))
    day = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    location = Column(String, nullable=True)

    course = relationship("Course", back_populates="timeslots")
