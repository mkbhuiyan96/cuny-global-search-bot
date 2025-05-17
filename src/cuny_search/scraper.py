import asyncio
from base64 import b64encode
from dataclasses import astuple
from bs4 import BeautifulSoup
from httpx import AsyncClient
from cuny_search.constants import COLLEGE_CODES, COLLEGE_BASE64, SESSION_BASE64, DEFAULT_INSTITUTION, HEADERS
from cuny_search.models import CourseParams, get_current_term_and_year


def encode_b64(s: str) -> str:
    return b64encode(s.encode()).decode()


def get_global_search_term_value(year: int, term: str) -> int:
    term_offsets = { "Spring Term": 2, "Summer Term": 6, "Fall Term": 9 }
    return (year-1900)*10 + term_offsets[term]


def get_schedule_builder_term_value(year: int, term: str) -> str:
    term_map = { "Spring Term": 10, "Summer Term": 20, "Fall Term": 30 }
    return f"320{year%100}{term_map[term]}"


async def refresh_client():
    while True:
        try:
            year, term = get_current_term_and_year()
            term_code = get_global_search_term_value(year, term)

            payload: dict[str, str] = {
                "selectedInstName": f"{DEFAULT_INSTITUTION} |",
                "inst_selection": COLLEGE_CODES[DEFAULT_INSTITUTION],
                "selectedTermName": f"{year} {term}",
                "term_value": str(term_code),
                "next_btn": "Next",
            }
            client = AsyncClient(headers=HEADERS)

            await client.post("https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController", data=payload)
            return client
        except Exception as e:
            print(f"Error while trying to create scraper session: {e}")
            await asyncio.sleep(2)


async def scrape(client: AsyncClient, course_params: CourseParams) -> BeautifulSoup:
    course_number, year, term, session, institution = astuple(course_params)
    term_code = get_global_search_term_value(year, term)

    params = {
        "class_number_searched": encode_b64(str(course_number)),
        "session_searched": SESSION_BASE64[session],
        "term_searched": encode_b64(str(term_code)),
        "inst_searched": COLLEGE_BASE64[institution]
    }

    response = await client.get("https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController", params=params)
    soup = BeautifulSoup(response.text, "lxml")
    return soup


if __name__ == "__main__":
    pass