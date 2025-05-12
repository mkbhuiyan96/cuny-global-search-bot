from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR/"data"

from .scraper import scrape
from .processor import process
from .create_db import initialize_tables
from . import access_db
from .discord_bot import start_bot
from . import discord_constants

__all__ = ["DATA_DIR", "scrape", "process", "initialize_tables", "access_db", "start_bot", "discord_constants"]