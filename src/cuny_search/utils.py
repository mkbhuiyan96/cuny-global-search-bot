from base64 import b64encode
from datetime import datetime


def encode_b64(s: str) -> str:
    return b64encode(s.encode()).decode()


def get_current_term_and_year() -> tuple[int, str]:
    now = datetime.now()

    if now.month <= 5:
        term = "Spring Term"
    elif now.month <= 8:
        term = "Summer Term"
    else:
        term = "Fall Term"
    return (now.year, term)


def get_global_search_term_value(year: int, term: str) -> int:
    term_offsets = { "Spring Term": 2, "Summer Term": 6, "Fall Term": 9 }
    return (year-1900)*10 + term_offsets[term]


def get_schedule_builder_term_value(year: int, term: str) -> str:
    term_map = { "Spring Term": 10, "Summer Term": 20, "Fall Term": 30 }
    return f"320{year%100}{term_map[term]}"