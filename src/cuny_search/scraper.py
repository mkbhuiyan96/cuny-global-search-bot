import asyncio
from bs4 import BeautifulSoup
from dataclasses import asdict
from httpx import AsyncClient
from icecream import ic
from cuny_search.constants import COLLEGE_CODES, DEFAULT_INSTITUTION, HEADERS
from cuny_search.models import CourseParams, EncodedParams
from cuny_search.utils import get_current_term_and_year, get_global_search_term_value


semaphore = asyncio.Semaphore(5)


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
            ic(f"Error while trying to create scraper session: {e}")
            await asyncio.sleep(2)


async def scrape(client: AsyncClient, params: CourseParams | EncodedParams) -> BeautifulSoup | None:
    if isinstance(params, EncodedParams):
        params = asdict(params)
    else:
        params = params.get_encoded_params()

    try:
        response = await client.get("https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController", params=params)
        soup = BeautifulSoup(response.text, "lxml")
        return soup
    except Exception as e:
        ic(f"Error while trying to scrape all courses for availability: {e}")
        return None


if __name__ == "__main__":
    pass