import asyncio
import os
from random import uniform
from typing import NoReturn
from dotenv import load_dotenv
import aiosqlite
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from icecream import ic
from cuny_search import DATA_DIR, refresh_client, initialize_tables, scrape, process
from cuny_search import access_db as db
from cuny_search.models import CourseDetails, CourseAvailabilities, EncodedParams


class Client(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.scraper = None
        self.semaphore = asyncio.Semaphore(5)

    async def refresh_scraper(self) -> None:
        if not self.scraper.is_closed:
            await self.scraper.aclose()
        self.scraper = await refresh_client()
        ic("Refreshed scraper client")

    async def setup_hook(self) -> None:
        await self.load_extension("cuny_search.discord_commands")
        async for guild in self.fetch_guilds():
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        # await self.tree.sync()  # Syncs the commands globally (has a rate limit)

    async def on_ready(self) -> None:
        ic(f"Logged on as {self.user}.")
        await initialize_tables()
        self.scraper = await refresh_client()
        await start_monitoring()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)


def status_changed(prev_status: str, new_status: str) -> bool:
    if prev_status == new_status:
        return False
    return "Open" in (prev_status, new_status)


async def start_monitoring() -> NoReturn:
    while True:
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            if await db.is_database_empty(conn):
                ic("Database is empty. Sleeping for 1 minute.")
                await asyncio.sleep(60)
                continue

            try:
                all_course_params = await db.fetch_all_course_params(conn)
            except Exception as e:
                ic(f"Error while trying to fetch all course params: {e}")
                continue

        uid_soup_pairs: list[tuple[int, BeautifulSoup]] = []
        for uid, *encoded_params in all_course_params:
            async with client.semaphore:
                try:
                    await asyncio.sleep(uniform(0.01, 0.2))
                    soup = await scrape(client.scraper, EncodedParams(*encoded_params))
                    if soup:
                        uid_soup_pairs.append((uid, soup))
                except Exception as e:
                    ic(f"Scrape failed for uid={uid}: {e}")
                    await client.refresh_scraper()

        all_processed_data: list[tuple[int, CourseDetails, CourseAvailabilities]] = []
        for uid, soup in uid_soup_pairs:
            try:
                course_details, course_availabilities = process(soup)
                all_processed_data.append((uid, course_details, course_availabilities))
            except Exception as e:
                ic(f"Processing failed for uid={uid}: {e}")

        try:
            async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
                await conn.execute("PRAGMA foreign_keys=ON")

                for uid, course_details, course_availabilities in all_processed_data:
                    prev_status = await db.update_course_availability(conn, uid, course_availabilities)
                    status = course_availabilities.status

                    if prev_status and status_changed(prev_status, status):
                        all_users_and_channels = await db.fetch_all_users_and_channels_for_course(conn, uid)

                        if status == "Open":
                            status_color = "\033[1;32m"
                        elif status == "Closed":
                            status_color = "\033[1;31m"
                        elif status == "Wait List":
                            status_color = "\033[1;33m"
                        else:
                            status_color = "\033[0m"

                        ansi_message = f"{course_details.course_name}-{course_details.course_number} is now {status_color}{status}\033[0m!"

                        for user_id, channel_id in all_users_and_channels:
                            channel = client.get_channel(int(channel_id))
                            if not channel:
                                channel = await client.fetch_channel(int(channel_id))
                            await channel.send(f"<@{user_id}>\n```ansi\n{ansi_message}\n```")
                            ic(f"Notified {user_id} in {channel_id} about {course_details.course_name}-{course_details.course_number} being {status}.")

                    ic(f"Course availability updated for: UID: {uid}, {course_details}, {course_availabilities}")
        except Exception as e:
            ic(f"An error occured while trying to update the course availability: {e}")

        await asyncio.sleep(uniform(3, 8))


def start_bot() -> None:
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        ic("Discord token not found! Cannot start bot.")


if __name__ == "__main__":
    start_bot()