import asyncio
import aiosqlite
import sys
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import cuny_search


async def main():
    await cuny_search.initialize_tables()
    course_params = (2025, "Fall Term", 49494)
    soup = await cuny_search.scrape(*course_params)
    course_details, course_availabilities = cuny_search.process(soup)

    async with aiosqlite.connect(cuny_search.DATA_DIR/"classes.db") as conn:
        await cuny_search.add_course(conn, course_params, course_details, course_availabilities)
    await cuny_search.start_bot()


if __name__ == "__main__":
    asyncio.run(main())