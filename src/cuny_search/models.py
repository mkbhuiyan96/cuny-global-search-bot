from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseParams:
    course_number: int
    year: int
    term: str
    session: Optional[str] = None
    institution: Optional[str] = None

    def __post_init__(self):
        self.course_number = int(self.course_number)
        self.year = int(self.year)

        if self.session is None:
            self.session = "Regular Academic Session"
        if self.institution is None:
            self.institution = "Queens College"


@dataclass
class CourseDetails:
    course_number: str
    course_name: str
    days_and_times: str
    room: str
    instructor: str
    meeting_dates: str


@dataclass
class CourseAvailabilities:
    course_number: int
    status: str
    course_capacity: str
    waitlist_capacity: str
    currently_enrolled: str
    currently_waitlisted: str
    available_seats: str

@dataclass
class UserInterests:
    course_number: int
    user_id: int
    channel_id: int