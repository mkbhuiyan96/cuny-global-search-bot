from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

from .scraper import refresh_client, scrape
from .processor import process
from .create_db import initialize_tables
from . import access_db
from . import constants
from . import models
from .discord_bot import start_bot


__all__ = [
    "DATA_DIR",
    "refresh_client",
    "scrape",
    "process",
    "initialize_tables",
    "access_db",
    "constants",
    "models",
    "start_bot"
]