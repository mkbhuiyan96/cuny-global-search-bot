from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR/"data"

from .scraper import scrape
from .processor import process
from .discord_bot import start_bot
from .create_db import initialize_tables
from .access_db import add_course_params, add_course_details, add_course_availabilities, add_course, remove_course, get_course_details, get_course_availability, update_course_availability, add_user_interest, remove_user_interest, fetch_user_interests, fetch_all_users_and_channels_for_course

__all__ = ["DATA_DIR", "scrape", "process", "start_bot", "initialize_tables", "add_course_params", "add_course", "add_course_details", "add_course_availabilities", "remove_course", "get_course_details", "get_course_availability", "update_course_availability", "add_user_interest", "remove_user_interest", "fetch_user_interests", "fetch_all_users_and_channels_for_course"]