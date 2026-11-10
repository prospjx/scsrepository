from pydantic import BaseModel, ConfigDict


class TimeslotBase(BaseModel):
    day: str
    start_time: str
    end_time: str
    location: str | None = None


class TimeslotResponse(TimeslotBase):
    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    course_id: str
    title: str
    credits: int
    description: str | None = None
    prerequisites: list[str] = []


class CourseResponse(CourseBase):
    timeslots: list[TimeslotResponse] = []
    model_config = ConfigDict(from_attributes=True)
