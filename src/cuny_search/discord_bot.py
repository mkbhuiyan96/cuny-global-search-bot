from dotenv import load_dotenv
import os
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
import cuny_search
from cuny_search import DATA_DIR
from cuny_search.discord_inputs import YEARS, TERMS, COURSE_NUMBERS, SESSIONS, INSTITUTIONS


class Client(commands.Bot):
    async def setup_hook(self):
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        await cuny_search.initialize_tables()
        print(f"Logged on as {self.user}!")


load_dotenv()
GUILD_ID = discord.Object(id=os.getenv("GUILD_ID"))
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)


@client.tree.command(name="add_course", description="Adds a course to be tracked by the bot.", guild=GUILD_ID)
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
    course_availability = None
    crn_string = str(course_number)

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            course_availability = await cuny_search.get_course_availability(conn, crn_string)
        except Exception as e:
            print(f"An error occured while trying to access the DB to verify course exists: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

        if not course_availability:
            course_tuple = tuple(c for c in (year, term, course_number, session, institution) if c)

            try:
                soup = await cuny_search.scrape(*course_tuple)
                course_details, course_availabilities = await cuny_search.process(soup)
                await cuny_search.add_course(conn, course_tuple, course_details, course_availabilities)
            except Exception as e:
                print(f"An error occured while trying to add a new course: {e}")
                await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
                return

        try:
            await cuny_search.add_user_interest(conn, (crn_string, interaction.user.id, interaction.channel.id))
            await interaction.response.send_message(f"Added {course_number} to your tracked courses.")
        except Exception as e:
            print(f"An error occured while trying to add a new user interest: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


@client.tree.command(name="remove_course", description="Stop tracking a course.", guild=GUILD_ID)
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def remove_course(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    num_remaining = None

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            num_remaining = await cuny_search.remove_user_interest(conn, interaction.user.id, str(course_number))
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


@client.tree.command(name="get_course_availability", description="Returns status of course and number of seats.", guild=GUILD_ID)
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def get_course_availability(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    course_availability = None

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            course_availability = await cuny_search.get_course_availability(conn, str(course_number))
        except Exception as e:
            print(f"An error occured while trying to access the DB for course availability: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

    if course_availability:
        status, course_capacity, waitlist_capacity, currently_enrolled, currently_waitlisted, available_seats = course_availability[4:]

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
            f"\033[1;34mStatus:\033[0m {status_color}{status}\033[0m\n"
            f"\033[1;34mEnrollment:\033[0m {currently_enrolled}/{course_capacity} students "
            f"({seats_color}{available_seats} seats available\033[0m)\n"
            f"\033[1;34mWaitlist:\033[0m {currently_waitlisted}/{waitlist_capacity} students"
        )
        await interaction.response.send_message(f"```ansi\n{message}\n```")
    else:
        await interaction.response.send_message("Class not found in database!")


@client.tree.command(name="get_course_details", description="Returns information such as time and professor for course provided.", guild=GUILD_ID)
@app_commands.describe(course_number="Unique Class Number that can be found on Schedule Builder or Global Search.")
async def get_course_details(interaction: discord.Interaction, course_number: COURSE_NUMBERS):
    course_details = None

    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            course_details = await cuny_search.get_course_details(conn, str(course_number))
        except Exception as e:
            print(f"An error occured while trying to access the DB for course availability: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            return

    if course_details:
        course_name, days_and_times, room, instructor, meeting_dates, = course_details[4:]
        message = (
            f"\033[1;33mClass:\033[0m {course_name}-{course_number}\n"
            f"\033[1;33mRoom:\033[0m {room}\n"
            f"\033[1;33mInstructor:\033[0m {instructor}\n"
            f"\033[1;32mSchedule:\033[0m This class will meet \033[3m{days_and_times}\033[0m, {meeting_dates}."
        )
        await interaction.response.send_message(f"```ansi\n{message}\n```")
    else:
        await interaction.response.send_message("Class not found in database!")


@client.tree.command(name="get_my_tracked_courses", description="Returns all the courses you are tracking.")
async def get_my_tracked_courses(interaction: discord.Interaction):
    pass


@client.tree.command(name="fetch_all_courses_tracked_by_bot", description="Returns a list of all the courses the bot is tracking for everyone.")
async def fetch_all_courses_tracked_by_bot(interaction: discord.Interaction):
    pass


def start_bot():
    client.run(os.getenv("DISCORD_TOKEN"))