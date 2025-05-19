from dataclasses import dataclass
from typing import Optional
from cuny_search.constants import SESSION_BASE64, COLLEGE_BASE64
from cuny_search.utils import get_current_term_and_year, get_global_search_term_value, encode_b64


class CourseParams:
    def __init__(
        self,
        course_number: int,
        term: Optional[str] = None,
        year: Optional[int] = None,
        session: Optional[str] = None,
        institution: Optional[str] = None
    ):
        self.course_number = str(course_number)

        current_year, current_term = get_current_term_and_year()
        self.year = int(year) if year is not None else current_year
        self.term = term or current_term
        self.term_code = str(get_global_search_term_value(self.year, self.term))

        self.session = session or "Regular Academic Session"
        self.institution = institution or "Queens College"

    def get_encoded_params(self) -> dict[str, str]:
        return {
            "class_number_searched": encode_b64(self.course_number),
            "session_searched": SESSION_BASE64[self.session],
            "term_searched": encode_b64(self.term_code),
            "inst_searched": COLLEGE_BASE64[self.institution]
        }

    def get_encoded_tuple(self) -> tuple[str, str, str, str]:
        return (
            encode_b64(self.course_number),
            SESSION_BASE64[self.session],
            encode_b64(self.term_code),
            COLLEGE_BASE64[self.institution]
        )


@dataclass
class EncodedParams:
    class_number_searched: str
    session_searched: str
    term_searched: str
    inst_searched: str


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
    status: str
    course_capacity: str
    waitlist_capacity: str
    currently_enrolled: str
    currently_waitlisted: str
    available_seats: str


@dataclass
class UserInterests:
    uid: int
    user_id: int
    channel_id: int