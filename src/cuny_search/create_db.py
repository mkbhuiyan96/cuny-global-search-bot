import aiosqlite
from icecream import ic
from cuny_search import DATA_DIR


async def initialize_tables() -> None:
    async with aiosqlite.connect(DATA_DIR/"classes.db") as conn:
        try:
            await conn.execute("PRAGMA foreign_keys=ON")

            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_params (
                        uid INTEGER PRIMARY KEY,
                        course_base64 TEXT NOT NULL,
                        session TEXT NOT NULL,
                        term_code TEXT NOT NULL,
                        institution TEXT NOT NULL,
                        UNIQUE (course_base64, session, term_code, institution)
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_details (
                        uid INTEGER PRIMARY KEY REFERENCES course_params(uid) ON DELETE CASCADE,
                        course_number TEXT,
                        course_name TEXT,
                        days_and_times TEXT,
                        room TEXT,
                        instructor TEXT,
                        meeting_dates TEXT
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course_availabilities (
                        uid INTEGER PRIMARY KEY REFERENCES course_params(uid) ON DELETE CASCADE,
                        status TEXT NOT NULL,
                        course_capacity TEXT,
                        waitlist_capacity TEXT,
                        currently_enrolled TEXT,
                        currently_waitlisted TEXT,
                        available_seats TEXT
                    )
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_interests (
                        uid INTEGER REFERENCES course_params(uid) ON DELETE CASCADE,
                        user_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        PRIMARY KEY (uid, user_id)
                    )
                """)
                await conn.commit()
                ic("Database successfully initialized.")

        except Exception as e:
            ic(f"Error occurred while initializing database: {e}")


if __name__ == "__main__":
    pass