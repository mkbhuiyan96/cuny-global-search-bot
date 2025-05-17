from datetime import datetime
from dataclasses import dataclass
from typing import Optional


def get_current_term_and_year() -> tuple[int, str]:
    now = datetime.now()

    if now.month <= 5:
        term = "Spring Term"
    elif now.month <= 8:
        term = "Summer Term"
    else:
        term = "Fall Term"
    return (now.year, term)

@dataclass
class CourseParams:
    course_number: int
    year: Optional[int] = None
    term: Optional[str] = None
    session: Optional[str] = None
    institution: Optional[str] = None

    def __post_init__(self):
        self.course_number = int(self.course_number)

        default_year, default_term = get_current_term_and_year()
        self.year = int(self.year) if self.year else default_year

        if not self.term:
            self.term = default_term
        if not self.session:
            self.session = "Regular Academic Session"
        if not self.institution:
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