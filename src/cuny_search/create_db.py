import aiosqlite
from cuny_search import DATA_DIR


async def initialize_tables() -> None:
    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            await conn.execute("PRAGMA foreign_keys=ON")

            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_params (
                        course_number TEXT PRIMARY KEY,
                        year TEXT,
                        term TEXT,
                        session TEXT,
                        institution TEXT
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_details (
                        course_number TEXT PRIMARY KEY REFERENCES course_params(course_number) ON DELETE CASCADE,
                        course_name TEXT,
                        days_and_times TEXT,
                        room TEXT,
                        instructor TEXT,
                        meeting_dates TEXT
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_availabilities (
                        course_number TEXT PRIMARY KEY REFERENCES course_params(course_number) ON DELETE CASCADE,
                        status TEXT,
                        course_capacity TEXT,
                        waitlist_capacity TEXT,
                        currently_enrolled TEXT,
                        currently_waitlisted TEXT,
                        available_seats TEXT
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_interests (
                        course_number TEXT REFERENCES course_params(course_number) ON DELETE CASCADE,
                        user_id TEXT,
                        channel_id TEXT,
                        PRIMARY KEY (user_id, course_number)
                    )
                """)
                await conn.commit()
                print("Database sucessfully initialized.")

        except Exception as e:
            print(f"Error occurred while initializing database: {e}")


if __name__ == "__main__":
    pass