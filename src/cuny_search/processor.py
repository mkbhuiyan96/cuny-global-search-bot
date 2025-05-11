import re

def process(soup: str) -> dict:
    div = soup.find("div", attrs={"class": "shadowbox"})
    details = div.find("p").get_text(strip=True)
    course_name = details.split(" - ")[0]

    td = soup.find("td", string=re.compile("Class Number"))
    course_number = td.find_next().get_text(strip=True)

    td = soup.find("img", title=["Open", "Close", "Wait"]).find_parent("td")
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

    data = {
        "course_name": course_name,
        "course_number": course_number,
        "status": status,
        "days_and_times": days_and_times,
        "room": room,
        "instructor": instructor,
        "meeting_dates": meeting_dates,
        "class_capacity": spans[0],
        "waitlist_capacity": spans[1],
        "currently_enrolled": spans[2],
        "currently_waitlisted": spans[3],
        "available_seats": spans[4]
    }
    return data