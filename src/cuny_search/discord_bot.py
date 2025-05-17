import asyncio
import os
from random import uniform
from typing import NoReturn
from dotenv import load_dotenv
import aiosqlite
import discord
from discord.ext import commands
from httpx import AsyncClient
from bs4 import BeautifulSoup
from cuny_search import DATA_DIR, refresh_client, initialize_tables, scrape, process
from cuny_search import access_db as db
from cuny_search.models import CourseParams, CourseDetails, CourseAvailabilities


class Client(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.scraper = AsyncClient()
        self.semaphore = asyncio.Semaphore(5)

    async def setup_hook(self) -> None:
        await self.load_extension("cuny_search.discord_commands")
        async for guild in self.fetch_guilds():
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        # await self.tree.sync()  # Syncs the commands globally (has a limit on how often this can be done)
        self.scraper = await refresh_client()

    async def on_ready(self) -> None:
        print(f"Logged on as {self.user}.")
        await start_monitoring()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)


def status_changed(prev_status: str, new_status: str) -> bool:
    if prev_status == new_status:
        return False
    return "Open" in (prev_status, new_status)


async def limited_scrape(params: CourseParams) -> BeautifulSoup:
    try:
        async with client.semaphore:
            await asyncio.sleep(uniform(0.01, 0.2))
            return await scrape(client.scraper, params)
    except Exception as e:
        print(f"Error while trying to scrape all courses for availability: {e}")
        client.scraper = await refresh_client()


async def start_monitoring() -> NoReturn:
    await initialize_tables()

    while True:
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

            if await db.is_database_empty(conn):
                print("Database is empty. Sleeping for 1 minute.")
                await asyncio.sleep(60)
                continue

            all_course_params = None
            try:
                all_course_params = await db.fetch_all_course_params(conn)
            except Exception as e:
                print(f"Error while trying to fetch all course params: {e}")
                continue

        tasks = [limited_scrape(CourseParams(*params)) for params in all_course_params]
        soups = await asyncio.gather(*tasks)

        all_processed_data: list[tuple[CourseDetails, CourseAvailabilities]] = []
        for soup in soups:
            if soup:
                all_processed_data.append(process(soup))

        try:
            async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
                await conn.execute("PRAGMA foreign_keys=ON")

                for course_details, course_availabilities in all_processed_data:
                    prev_status = await db.update_course_availability(conn, course_availabilities)

                    if prev_status and status_changed(prev_status, course_availabilities.status):
                        all_users_and_channels = await db.fetch_all_users_and_channels_for_course(conn, course_availabilities.course_number)

                        for user_id, channel_id in all_users_and_channels:
                            channel = client.get_channel(int(channel_id))
                            if not channel:
                                channel = await client.fetch_channel(int(channel_id))
                            await channel.send(f"<@{user_id}>, {course_details.course_name}-{course_details.course_number} is now {course_availabilities.status}!")
                            print(f'Notified {user_id} in {channel_id} about {course_details.course_name}-{course_details.course_number} being {course_availabilities.status}.')

                    print(f"Course availability updated for: {course_availabilities}")
        except Exception as e:
            print(f"An error occured while trying to update the course availability: {e}")

        await asyncio.sleep(uniform(1, 7))


def start_bot():
    load_dotenv()
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    start_bot()