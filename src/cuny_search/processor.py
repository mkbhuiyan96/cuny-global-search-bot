from cuny_search.models import CourseDetails, CourseAvailabilities
from bs4 import BeautifulSoup, Tag, NavigableString
import re
from typing import Any


def safe_find(soup: BeautifulSoup, tag: str, *args: Any, **kwargs: Any) -> Tag | NavigableString:
    result = soup.find(tag, *args, **kwargs)
    if not result:
        raise ValueError(f"Could not find tag: {tag} with {kwargs}")
    return result

def safe_find_next(soup: BeautifulSoup, el: Tag, *args: Any, **kwargs: Any) -> Tag | NavigableString:
    result = el.find_next(*args, **kwargs)
    if not result:
        raise ValueError(f"Could not find next tag from element: {el} with {kwargs}")
    return result


def process(soup: BeautifulSoup) -> tuple[CourseDetails, CourseAvailabilities]:
    div = safe_find(soup, "div", attrs={"class": "shadowbox"})
    p = div.find("p")
    if not p:
        raise ValueError("Could not find <p> tag in shadowbox")

    details = p.get_text(strip=True)
    course_name = details.split(" - ")[0]

    td = safe_find(soup, "td", string=re.compile("Class Number"))
    course_number = safe_find_next(soup, td).get_text(strip=True)

    img_td = soup.find("img", title=["Open", "Closed", "Wait"])
    if not img_td:
        raise ValueError("Could not find <img> with status title")

    status_td = img_td.find_parent("td")
    if not status_td:
        raise ValueError("Could not find parent <td> of status <img>")
    status = status_td.get_text(strip=True)

    def get_data_label(label: str):
        td = soup.find("td", attrs={"data-label": label})
        if not td:
            raise ValueError(f"Could not find <td> with data-label '{label}'")
        return td.get_text(strip=True)

    days_and_times = get_data_label("Days And Times")
    room = get_data_label("Room")
    instructor = get_data_label("Instructor")
    meeting_dates = get_data_label("Meeting Dates")

    availability_header = soup.find("b", string=re.compile("Class Availability"))
    if not availability_header:
        raise ValueError("Could not find bolded 'Class Availability' header")

    availability_table = availability_header.find_next("table")
    if not availability_table:
        raise ValueError("Could not find availability table after 'Class Availability' header")

    spans = availability_table.find_all("span")
    if len(spans) < 5:
        raise ValueError(f"Expected 5 spans in availability table but found {len(spans)}")
    span_values = [span.get_text(strip=True) for span in spans[:5]]

    course_details = CourseDetails(
        course_number=course_number,
        course_name=course_name,
        days_and_times=days_and_times,
        room=room,
        instructor=instructor,
        meeting_dates=meeting_dates
    )

    course_availabilities = CourseAvailabilities(
        course_number=course_number,
        status=status,
        course_capacity=span_values[0],
        waitlist_capacity=span_values[1],
        currently_enrolled=span_values[2],
        currently_waitlisted=span_values[3],
        available_seats=span_values[4]
    )

    return course_details, course_availabilities


if __name__ == "__main__":
    pass