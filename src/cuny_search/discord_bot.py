from dotenv import load_dotenv
import os
import aiosqlite
import discord
import asyncio
from random import uniform
from discord import app_commands
from discord.ext import commands
import cuny_search
from cuny_search import DATA_DIR
from cuny_search import access_db as db
from cuny_search.models import CourseParams, UserInterests
from cuny_search.constants import YEARS, TERMS, COURSE_NUMBERS, SESSIONS, INSTITUTIONS, HEADERS


class Client(commands.Bot):
    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.scraper = None

    async def setup_hook(self):
        async for guild in self.fetch_guilds():
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        self.scraper = await cuny_search.refresh_client()
        # try:
        #     synced = await self.tree.sync()
        #     print(f"Synced {len(synced)} commands!")
        # except Exception as e:
        #     print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f"Logged on as {self.user}.")
        await start_monitoring()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)


async def start_monitoring():
    await cuny_search.initialize_tables()
    semaphore = asyncio.Semaphore(5)

    while True:
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
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


        async def limited_scrape(params):
            async with semaphore:
                await asyncio.sleep(uniform(0.01, 0.2))
                return await cuny_search.scrape(client.scraper, params)

        tasks = [limited_scrape(CourseParams(*params)) for params in all_course_params]
        soups = await asyncio.gather(*tasks)

        all_course_details, all_course_availabilities = [], []
        for soup in soups:
            course_details, course_availabilities = cuny_search.process(soup)
            all_course_details.append(course_details)
            all_course_availabilities.append(course_availabilities)

        try:
            async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
                for course_availabilities in all_course_availabilities:
                    await db.update_course_availability(conn, course_availabilities)
                    print(f"Course availability updated for: {course_availabilities}")
        except Exception as e:
            print(f"An error occured while trying to update the course availability: {e}")

        await asyncio.sleep(uniform(1, 7))



@client.tree.command(name="add_course", description="Adds a course to be tracked by the bot.")
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
@app_commands.describe(session="Length of the class. Typically required for Summer or Winter courses.")
@app_commands.describe(institution="Name of the college. Usually not required.")
async def add_course(
    interaction: discord.Interaction,
    year: YEARS,
    term: TERMS,
    course_number: COURSE_NUMBERS,
    session: SESSIONS,
    institution: INSTITUTIONS
):
    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        already_added = False
        try:
            already_added = await db.is_course_in_user_interests(conn, course_number, interaction.user.id)
        except Exception as e:
            print(f"An error occured while trying to access the DB to check if user already added the course: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

        if already_added:
            await interaction.response.send_message(f"You are already tracking this course!", ephemeral=True)
            return

        course_params = None

        try:
            course_params = await db.get_course_params(conn, course_number)
        except Exception as e:
            print(f"An error occured while trying to access the DB to verify course exists: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

        if not course_params: # Course wasn't found, need to scrape
            course_params = CourseParams(course_number, year, term, session, institution)
            try:
                soup = await cuny_search.scrape(client.scraper, course_params)
                course_details, course_availabilities = cuny_search.process(soup)
                await db.add_course_params(conn, course_params)
                await db.add_course_details(conn, course_details)
                await db.add_course_availability(conn, course_availabilities)
            except Exception as e:
                print(f"An error occured while trying to add a new course: {e}")
                await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
                return

        try:
            await db.add_user_interest(conn, UserInterests(course_number, interaction.user.id, interaction.channel.id))
            await interaction.response.send_message(f"Added {course_number} to your tracked courses.")
        except Exception as e:
            print(f"An error occured while trying to add a new user interest: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


@client.tree.command(name="remove_course", description="Stop tracking a course.")
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def remove_course(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    num_remaining = -1

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            num_remaining = await db.remove_user_interest(conn, interaction.user.id, course_number)
            if num_remaining == -1:
                raise ValueError("Was not able to successfully select a row during deletion")
        except Exception as e:
            print(f"An error occured while accessing the DB to remove a course: {e}")
            await interaction.response.send_message(f"An error occured: {e}", ephemeral=True)
            return

    message = f"Successfully removed {course_number}."
    if num_remaining == 0:
        message += "\nNo one else was tracking this course, so it was removed from the database."
    await interaction.response.send_message(message)


@client.tree.command(name="get_course_availability", description="Returns status of course and number of seats.")
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def get_course_availability(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    course_availability = None

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            course_availability = await db.get_course_availability(conn, course_number)
        except Exception as e:
            print(f"An error occured while trying to access the DB for course availability: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

    if course_availability:
        status, course_capacity, waitlist_capacity, currently_enrolled, currently_waitlisted, available_seats = course_availability[6:]

        if status == "Open":
            status_color = "\033[1;32m"
        elif status == "Closed":
            status_color = "\033[1;31m"
        elif status == "Wait List":
            status_color = "\033[1;33m"
        else:
            status_color = "\033[0m"
        seats_color = "\033[1;32m" if int(available_seats) > 0 else "\033[1;31m"

        message = (
            f"\033[1;36mStatus:\033[0m {status_color}{status}\033[0m\n"
            f"\033[1;36mEnrollment:\033[0m {currently_enrolled}/{course_capacity} students "
            f"({seats_color}{available_seats} seats available\033[0m)\n"
            f"\033[1;36mWaitlist:\033[0m {currently_waitlisted}/{waitlist_capacity} students"
        )
        await interaction.response.send_message(f"```ansi\n{message}\n```")
    else:
        await interaction.response.send_message("Class not found in database!")


@client.tree.command(name="get_course_details", description="Returns information such as time and professor for course provided.")
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def get_course_details(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    course_details = None

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            course_details = await db.get_course_details(conn, course_number)
        except Exception as e:
            print(f"An error occured while trying to access the DB for course availability: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

    if course_details:
        course_name, days_and_times, room, instructor, meeting_dates, = course_details[6:]
        message = (
            f"\033[1;36mClass:\033[0m {course_name}-\u001b[34m{course_number}\u001b[0m\n"
            f"\033[1;36mRoom:\033[0m {room}\n"
            f"\033[1;36mInstructor:\033[0m {instructor}\n"
            f"\033[1;36mSchedule:\033[0m This class will meet \033[3m{days_and_times}\033[0m, {meeting_dates}."
        )
        await interaction.response.send_message(f"```ansi\n{message}\n```")
    else:
        await interaction.response.send_message("Class not found in database!")


@client.tree.command(name="get_my_tracked_courses", description="Returns all the courses you are tracking.")
async def get_my_tracked_courses(interaction: discord.Interaction):
    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            rows = await db.fetch_user_interests(conn, interaction.user.id)
            if rows:
                lines = []
                for row in rows:
                    course_name = row[4]
                    course_number = row[3]
                    days_and_times = row[5]
                    professor = row[7] if row[7] else "No professor assigned"

                    lines.append(
                        f"\u001b[1;36mClass:\u001b[0m {course_name}-\u001b[34m{course_number}\u001b[0m\n"
                        f"  \u001b[1;36mDays & Times:\u001b[0m {days_and_times}\n"
                        f"  \u001b[1;36mInstructor:\u001b[0m {professor}"
                    )

                ansi_block = "```ansi\n" + "\n\n".join(lines) + "\n```"
                await interaction.response.send_message(ansi_block)
            else:
                await interaction.response.send_message("You aren't tracking any courses!", ephemeral=True)
        except Exception as e:
            print(f"An error occured while trying to access the DB to get {interaction.user.id}'s tracked courses: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


@client.tree.command(name="fetch_all_courses_tracked_by_bot", description="Returns a list of all the courses the bot is tracking for everyone.")
async def fetch_all_courses_tracked_by_bot(interaction: discord.Interaction):
    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            rows = await db.fetch_all_course_numbers_and_names(conn)
            if rows:
                lines = []
                for row in rows:
                    lines.append(f"{row[1]}-\u001b[34m{row[0]}\u001b[0m")

                ansi_block = "```ansi\n" + "\n".join(lines) + "\n```"
                await interaction.response.send_message(ansi_block)
            else:
                await interaction.response.send_message("No courses are being tracked by the bot!")
        except Exception as e:
            print(f"An error occured while trying to access the DB to get all courses: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


def start_bot():
    load_dotenv()
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    start_bot()