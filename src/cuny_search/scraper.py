from cuny_search import DATA_DIR
import yaml
import httpx
from bs4 import BeautifulSoup
from base64 import b64encode
from typing import Optional


session_b64, college_b64, college_codes = None, None, None
DEFAULT_SESSION = "Regular Academic Session"
DEFAULT_INSTITUTION = "Queens College"


def load_config():
    global session_b64, college_b64, college_codes
    if session_b64: # Files already loaded
        return

    with open(DATA_DIR/"session_b64.yaml", "r") as file:
        session_b64 = yaml.safe_load(file)
    with open(DATA_DIR/"college_b64.yaml", "r") as file:
        college_b64 = yaml.safe_load(file)
    with open(DATA_DIR/"college_codes.yaml", "r") as file:
        college_codes = yaml.safe_load(file)


def encode_b64(s: str) -> str:
    return b64encode(s.encode()).decode()


def get_term_value(year: int, term: str) -> int:
    term_offsets = { "Spring Term": 2, "Summer Term": 6, "Fall Term": 9 }
    return (year-1900)*10 + term_offsets[term]


async def scrape(year: int, term: str, course_number: int, session: Optional[str] = None, institution: Optional[str] = None) -> BeautifulSoup:
    load_config()
    if not session:
        session = DEFAULT_SESSION
    if not institution:
        institution = DEFAULT_INSTITUTION
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36" }
    term_code = get_term_value(year, term)

    term_payload = {
        "selectedInstName": f"{institution} |",
        "inst_selection": college_codes[institution],
        "selectedTermName": f"{year} {term}",
        "term_value": term_code,
        "next_btn": "Next",
    }
    class_payload = {
        "class_number_searched": encode_b64(str(course_number)),
        "session_searched": session_b64[session],
        "term_searched": encode_b64(str(term_code)),
        "inst_searched": college_b64[institution]
    }

    async with httpx.AsyncClient(headers=headers) as client:
        # Initial post to establish session cookies
        await client.post("https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController", params=term_payload)
        response = await client.get("https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController", params=class_payload)

        soup = BeautifulSoup(response.text, "lxml")
    return soup


if __name__ == "__main__":
    load_config()