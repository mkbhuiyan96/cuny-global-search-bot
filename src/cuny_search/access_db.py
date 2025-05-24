from collections.abc import Iterable
from dataclasses import astuple
from aiosqlite import Connection, Row
from icecream import ic
from cuny_search.constants import AMBIGUOUS, NOT_FOUND
from cuny_search.models import CourseParams, CourseAvailabilities, CourseDetails, UserInterests


async def is_database_empty(conn: Connection) -> bool:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM course_params LIMIT 1")
            result = await cursor.fetchone()
            return result is None
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all courses: {e}")
        return True


async def get_or_create_uid(conn: Connection, course_params: CourseParams) -> tuple[int | None, bool]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT uid
                FROM course_params
                WHERE course_base64 = ? AND session = ? AND term_code = ? AND institution = ?
            """, course_params.get_encoded_tuple())
            row = await cursor.fetchone()
            if row:
                return (row[0], False)

            await cursor.execute("""
                INSERT INTO course_params (course_base64, session, term_code, institution)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(course_base64, session, term_code, institution) DO NOTHING
            """, course_params.get_encoded_tuple())
            await conn.commit()

            uid = cursor.lastrowid
            ic(f"Added new course: {course_params.course_number} with UID: {uid}")
            return (uid, True) if uid else (None, False)
    except Exception as e:
        ic(f"DB error occurred during upsert for {course_params.get_encoded_params()}: {e}")
        return (None, False)


async def get_unique_uid(conn: Connection, course_params) -> int:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT uid
                FROM course_params
                WHERE course_base64 = ?
            """, (course_params.get_encoded_tuple()[0],))
            rows = await cursor.fetchall()

            await cursor.execute("""
                SELECT uid
                FROM course_params
                WHERE course_base64 = ? AND session = ? AND term_code = ? AND institution = ?
            """, course_params.get_encoded_tuple())
            row = await cursor.fetchone()

            if not row:
                # If there are multiple rows found then the user probably needs to be more specific with their query
                return AMBIGUOUS if len(rows) > 1 else NOT_FOUND
            return row[0]
    except Exception as e:
        ic(f"An error occured while trying to get unique uid: {course_params}")
        return NOT_FOUND


async def add_course_details(conn: Connection, uid: int, course_details: CourseDetails) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO course_details VALUES (?, ?, ?, ?, ?, ?, ?)", (uid, *astuple(course_details)))
            await conn.commit()
    except Exception as e:
        ic(f"DB error occurred while attempting to add course details {course_details}: {e}")


async def add_course_availability(conn: Connection, uid: int, course_availabilities: CourseAvailabilities) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO course_availabilities VALUES (?, ?, ?, ?, ?, ?, ?)", (uid, *astuple(course_availabilities)))
            await conn.commit()
    except Exception as e:
        ic(f"DB error occurred while attempting to add course availabilities {course_availabilities}: {e}")


async def get_course_details(conn: Connection, course_params: CourseParams) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            uid = await get_unique_uid(conn, course_params)
            if uid < 0:
                raise ValueError("Error while trying to query for specified course in course details")

            await cursor.execute("""
                SELECT *
                FROM course_details
                WHERE course_details.uid = ?
            """, (uid,))
            return await cursor.fetchone()
    except Exception as e:
        ic(f"Error occurred while trying to get course details for {uid}: {e}")
        return None


async def get_course_availability(conn: Connection, course_params: CourseParams) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            uid = await get_unique_uid(conn, course_params)
            if uid < 0:
                raise ValueError("Error while trying to query for specified course in course availability")

            await cursor.execute("""
                SELECT *
                FROM course_availabilities
                WHERE course_availabilities.uid = ?
            """, (uid,))
            return await cursor.fetchone()
    except Exception as e:
        ic(f"Error occurred while trying to get course and details for {course_params}: {e}")
        return None


async def update_course_availability(conn: Connection, uid: int, course_availabilities: CourseAvailabilities) -> str | None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT status FROM course_availabilities WHERE uid = ?
            """, (uid,))
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
                WHERE uid = ?
            """, (*astuple(course_availabilities), uid))
            await conn.commit()
            return prev_status[0] if prev_status else None
    except Exception as e:
        ic(f"Error occurred while trying to update {course_availabilities}: {e}")
        return None


async def fetch_all_course_params(conn: Connection) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM course_params")
            return await cursor.fetchall()
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all course params: {e}")
        return []


async def fetch_all_course_numbers_and_names(conn: Connection) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT course_number, course_name FROM course_details")
            return await cursor.fetchall()
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all course numbers and names: {e}")
        return []


async def add_user_interest(conn: Connection, user_interests: UserInterests) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO user_interests VALUES (?, ?, ?)", astuple(user_interests))
            await conn.commit()
    except Exception as e:
        ic(f"DB error occurred while attempting to add user interest {user_interests}: {e}")


async def remove_user_interest(conn: Connection, course_params: CourseParams, user_id: int) -> int:
    try:
        async with conn.cursor() as cursor:
            uid = await get_unique_uid(conn, course_params)
            if uid < 0:
                return uid

            await cursor.execute("DELETE FROM user_interests WHERE uid = ? AND user_id = ?", (uid, user_id))
            if cursor.rowcount == 0:
                return NOT_FOUND

            await cursor.execute("SELECT COUNT(*) FROM user_interests WHERE uid = ?", (uid,))
            remaining_users_interested = await cursor.fetchone()
            if not remaining_users_interested:
                return NOT_FOUND

            if remaining_users_interested[0] == 0:
                await cursor.execute("DELETE FROM course_params WHERE uid = ?", (uid,))
            await conn.commit()
            return remaining_users_interested[0]
    except Exception as e:
        ic(f"Error while removing interest for {course_params}, user_id={user_id}: {e}")
        return NOT_FOUND


async def is_course_in_user_interests(conn: Connection, uid: int, user_id: int) -> bool:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT 1 FROM user_interests WHERE uid = ? AND user_id = ? LIMIT 1",
                (uid, user_id)
            )
            result = await cursor.fetchone()
            return result is not None
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all user interests: {e}")
        return False


async def fetch_user_interests(conn: Connection, user_id: int) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT *
                FROM user_interests
                JOIN course_details ON user_interests.uid = course_details.uid
                WHERE user_interests.user_id = ?
            """, (user_id,))
            return await cursor.fetchall()
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all user interests: {e}")
        return []


async def fetch_all_users_and_channels_for_course(conn: Connection, uid: int) -> Iterable[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT user_id, channel_id FROM user_interests WHERE uid = ?", (uid,))
            return await cursor.fetchall()
    except Exception as e:
        ic(f"DB error occurred while attempting to fetch all users interested in {uid}: {e}")
        return []


if __name__ == "__main__":
    pass