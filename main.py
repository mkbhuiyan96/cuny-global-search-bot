import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent / "src"))
import cuny_search
from bs4 import BeautifulSoup
import asyncio



if __name__ == "__main__":
    # scrape(2025, "Fall Term", 49494)
    # start_bot()

    with open(cuny_search.DATA_DIR/"output.html", "r") as file:
        soup = BeautifulSoup(file.read(), "lxml")

    data = cuny_search.process(soup)
    print(data)

    asyncio.run(cuny_search.initialize_tables())