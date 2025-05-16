from cuny_search.models import CourseParams, CourseAvailabilities, CourseDetails, UserInterests
from aiosqlite import Connection, Row
from dataclasses import astuple
from collections.abc import Iterable


async def is_database_empty(conn: Connection) -> bool:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM course_params LIMIT 1")
            result = await cursor.fetchone()
            return result is None
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all courses: {e}")
        return True


async def add_course_params(conn: Connection, course_params: CourseParams) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO course_params VALUES (?, ?, ?, ?, ?)", astuple(course_params))
            await conn.commit()
    except Exception as e:
        print(f"DB error occurred while attempting to add course {course_params}: {e}")


async def add_course_details(conn: Connection, course_details: CourseDetails) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO course_details VALUES (?, ?, ?, ?, ?, ?)", astuple(course_details))
            await conn.commit()
    except Exception as e:
        print(f"DB error occurred while attempting to add course details {course_details}: {e}")


async def add_course_availability(conn: Connection, course_availabilities: CourseAvailabilities) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO course_availabilities VALUES (?, ?, ?, ?, ?, ?, ?)", astuple(course_availabilities))
            await conn.commit()
    except Exception as e:
        print(f"DB error occurred while attempting to add course availabilities {course_availabilities}: {e}")


async def get_course_params(conn: Connection, course_number: int) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM course_params WHERE course_number = ?", (course_number,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"DB error occurred while attempting to get params for {course_number}: {e}")
        return None


async def get_course_details(conn: Connection, course_number: int) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT *
                FROM course_params
                JOIN course_details ON course_params.course_number = course_details.course_number
                WHERE course_details.course_number = ?
            """, (course_number,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error occurred while trying to get course details for {course_number}: {e}")
        return None


async def get_course_availability(conn: Connection, course_number: int) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT *
                FROM course_params
                JOIN course_availabilities ON course_params.course_number = course_availabilities.course_number
                WHERE course_availabilities.course_number = ?
            """, (course_number,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error occurred while trying to get course and details for {course_number}: {e}")
        return None


async def update_course_availability(conn: Connection, course_availaibilites: CourseAvailabilities) -> str | None:
    availability_tuple = astuple(course_availaibilites)[1:] + (course_availaibilites.course_number, )

    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT status FROM course_availabilities WHERE course_number = ?
            """, (course_availaibilites.course_number,))
            prev_status = await cursor.fetchone()

            await cursor.execute("""
                UPDATE course_availabilities
                SET
                    status = ?,
                    course_capacity = ?,
                    waitlist_capacity = ?,
                    currently_enrolled = ?,
                    currently_waitlisted = ?,
                    available_seats = ?
                WHERE course_number = ?
            """, (availability_tuple))
            await conn.commit()
            return prev_status[0] if prev_status else None
    except Exception as e:
        print(f"Error occurred while trying to update {course_availaibilites}: {e}")
        return None


async def fetch_all_course_params(conn: Connection) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM course_params")
            return await cursor.fetchall()
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all course params: {e}")
        return []


async def fetch_all_course_numbers_and_names(conn: Connection) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT course_number, course_name FROM course_details")
            return await cursor.fetchall()
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all course numbers and names: {e}")
        return []


async def add_user_interest(conn: Connection, user_interests: UserInterests) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO user_interests VALUES (?, ?, ?)", astuple(user_interests))
            await conn.commit()
    except Exception as e:
        print(f"DB error occurred while attempting to add user interest {user_interests}: {e}")


async def remove_user_interest(conn: Connection, user_id: int, course_number: int) -> int:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM user_interests WHERE user_id = ? AND course_number = ?", (user_id, course_number))
            if cursor.rowcount == 0:
                return -1

            await cursor.execute("SELECT COUNT(*) FROM user_interests WHERE course_number = ?", (course_number,))
            remaining_users_interested = await cursor.fetchone()
            if not remaining_users_interested:
                return -1

            if remaining_users_interested[0] == 0:
                await cursor.execute("DELETE FROM course_params WHERE course_number = ?", (course_number,))

            await conn.commit()
            return remaining_users_interested[0]
    except Exception as e:
        print(f"DB error occurred while attempting to remove a user interest for {course_number}: {e}")
        return -1


async def is_course_in_user_interests(conn: Connection, course_number: int, user_id: int) -> bool:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT 1 FROM user_interests WHERE course_number = ? AND user_id = ? LIMIT 1",
                (course_number, user_id)
            )
            result = await cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all user interests: {e}")
        return False


async def fetch_user_interests(conn: Connection, user_id: int) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT *
                FROM user_interests
                JOIN course_details ON user_interests.course_number = course_details.course_number
                WHERE user_interests.user_id = ?
            """, (user_id,))
            return await cursor.fetchall()
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all user interests: {e}")
        return []


async def fetch_all_users_and_channels_for_course(conn: Connection, course_number: int) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT user_id, channel_id FROM user_interests WHERE course_number = ?", (course_number,))
            return await cursor.fetchall()
    except Exception as e:
        print(f"DB error occurred while attempting to fetch all users interested in {course_number}: {e}")
        return []


if __name__ == "__main__":
    pass