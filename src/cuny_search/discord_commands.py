import aiosqlite
from discord import Interaction, app_commands
from discord.ext import commands
from cuny_search import DATA_DIR, process, scrape
from cuny_search import access_db as db
from cuny_search.constants import YEARS, TERMS, COURSE_NUMBERS, SESSIONS, INSTITUTIONS
from cuny_search.models import CourseParams, UserInterests


class CourseCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add_course", description="Adds a course to be tracked by the bot.")
    @app_commands.describe(course_number="Unique Class Number that can be found on Global Search or Schedule Builder.")
    @app_commands.describe(year="Defaults to current year.")
    @app_commands.describe(term="Defaults to current term.")
    @app_commands.describe(session="Typically required for Summer or Winter courses. Defaults to Regular Academic Session.")
    @app_commands.describe(institution="Name of the college. Defaults to Queens College.")
    async def add_course(self, interaction: Interaction, course_number: COURSE_NUMBERS, year: YEARS, term: TERMS, session: SESSIONS, institution: INSTITUTIONS):
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")
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
                    soup = await scrape(self.bot.scraper, course_params)
                    course_details, course_availabilities = process(soup)

                    if course_details.course_number != str(course_number):
                        raise ValueError(f"Mismatched course number: expected {course_number}, got {course_details.course_number}. Most likely malformed course info.")

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


    @app_commands.command(name="remove_course", description="Stop tracking a course.")
    @app_commands.describe(course_number="Unique Class Number that can be found on Global Search or Schedule Builder.")
    async def remove_course(self, interaction: Interaction, course_number: COURSE_NUMBERS):
        num_remaining = -1

        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

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


    @app_commands.command(name="get_course_availability", description="Returns status of course and number of seats.")
    @app_commands.describe(course_number="Unique Class Number that can be found on Global Search or Schedule Builder.")
    async def get_course_availability(self, interaction: Interaction, course_number: COURSE_NUMBERS):
        course_availability = None

        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

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


    @app_commands.command(name="get_course_details", description="Returns information such as meet times and professor.")
    @app_commands.describe(course_number="Unique Class Number that can be found on Global Search or Schedule Builder.")
    async def get_course_details(self, interaction: Interaction, course_number: COURSE_NUMBERS):
        course_details = None

        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

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


    @app_commands.command(name="get_my_tracked_courses", description="Returns all the courses you are tracking.")
    async def get_my_tracked_courses(self, interaction: Interaction):
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

            try:
                rows = await db.fetch_user_interests(conn, interaction.user.id)
                if rows:
                    lines: list[str] = []
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


    @app_commands.command(name="fetch_all_courses_tracked_by_bot", description="Returns all the courses the bot is tracking for everyone.")
    async def fetch_all_courses_tracked_by_bot(self, interaction: Interaction):
        async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
            await conn.execute("PRAGMA foreign_keys=ON")

            try:
                rows = await db.fetch_all_course_numbers_and_names(conn)
                if rows:
                    lines: list[str] = []
                    for row in rows:
                        lines.append(f"{row[1]}-\u001b[34m{row[0]}\u001b[0m")

                    ansi_block = "```ansi\n" + "\n".join(lines) + "\n```"
                    await interaction.response.send_message(ansi_block)
                else:
                    await interaction.response.send_message("No courses are being tracked by the bot!")
            except Exception as e:
                print(f"An error occured while trying to access the DB to get all courses: {e}")
                await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CourseCommands(bot))


if __name__ == "__main__":
    pass