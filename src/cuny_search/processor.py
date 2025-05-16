from cuny_search.models import CourseDetails, CourseAvailabilities
from bs4 import BeautifulSoup
import re


def process(soup: BeautifulSoup) -> tuple[CourseDetails, CourseAvailabilities]:
    div = soup.find("div", attrs={"class": "shadowbox"})
    details = div.find("p").get_text(strip=True)
    course_name = details.split(" - ")[0]

    td = soup.find("td", string=re.compile("Class Number"))
    course_number = td.find_next().get_text(strip=True)

    td = soup.find("img", title=["Open", "Closed", "Wait"]).find_parent("td")
    status = td.get_text(strip=True)

    td = soup.find("td", attrs={"data-label": "Days And Times"})
    days_and_times = td.get_text(strip=True)

    td = soup.find("td", attrs={"data-label": "Room"})
    room = td.get_text(strip=True)

    td = soup.find("td", attrs={"data-label": "Instructor"})
    instructor = td.get_text(strip=True)

    td = soup.find("td", attrs={"data-label": "Meeting Dates"})
    meeting_dates = td.get_text(strip=True)

    availability_table = soup.find("b", string=re.compile("Class Availability")).find_next("table")
    spans = availability_table.find_all("span")
    spans = [span.get_text(strip=True) for span in spans]

    course_details = CourseDetails(course_number, course_name, days_and_times, room, instructor, meeting_dates)
    course_availabilities = CourseAvailabilities(course_number, status, spans[0], spans[1], spans[2], spans[3], spans[4])
    return (course_details, course_availabilities)


if __name__ == "__main__":
    pass