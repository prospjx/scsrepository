import uuid

from sqlalchemy import JSON, Column, String

from src.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String, nullable=False)

    # Store all flexible preferences as a single JSON object in the database
    preferences = Column(JSON, nullable=False)
