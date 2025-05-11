from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR/"data"

from .scraper import scrape
from .processor import process
from .discord_bot import start_bot
from .create_db import initialize_tables
from .access_db import add_course, remove_course, fetch_all_courses, update_course_availability, get_course_details, add_user_interest, remove_user_interest, fetch_user_interests, fetch_all_users_and_channels_for_course

__all__ = ["DATA_DIR", "scrape", "process", "start_bot", "initialize_tables", "add_course", "remove_course", "fetch_all_courses", "update_course_availability", "get_course_details", "add_user_interest", "remove_user_interest", "fetch_user_interests", "fetch_all_users_and_channels_for_course"]