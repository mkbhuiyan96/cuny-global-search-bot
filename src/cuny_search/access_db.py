from aiosqlite import Connection, Row

async def is_database_empty(conn: Connection) -> Row | None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT 1 FROM course_params LIMIT 1')
            return cursor.fetchone()
    except Exception as e:
        print(f'DB error occurred while attempting to fetch all courses: {e}')
        return None


async def add_course_params(conn: Connection, course_tuple: tuple[str, str, str]) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_params VALUES (?, ?, ?)', course_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course {course_tuple}: {e}')


async def add_course_details(conn: Connection, details_tuple: tuple[str, str, str, str, str, str]) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_details VALUES (?, ?, ?, ?, ?, ?)', details_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course details {details_tuple}: {e}')


async def add_course_availability(conn: Connection, availabilities_tuple: tuple[str, str, str, str, str, str, str]) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_availabilities VALUES (?, ?, ?, ?, ?, ?, ?)', availabilities_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course availabilities {availabilities_tuple}: {e}')


async def add_course(conn: Connection, course_tuple: tuple, course_details: dict[str, str], course_availabilities: dict[str, str]) -> None:
    if len(course_tuple) > 3:
        course_tuple = course_tuple[:3]
    details_tuple = tuple(course_details.values())
    availabilities_tuple = tuple(course_availabilities.values())

    await add_course_params(conn, course_tuple)
    await add_course_details(conn, details_tuple)
    await add_course_availability(conn, availabilities_tuple)


async def remove_course(conn: Connection, course_number: str) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM course_params WHERE course_number = ?', (course_number,))
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to remove course_number {course_number}: {e}')


async def get_course_details(conn: Connection, course_number: str) -> Row | None:
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
        print(f'Error occurred while trying to get course and details for {course_number}: {e}')
        return None


async def get_course_availability(conn: Connection, course_number: str) -> Row | None:
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
        print(f'Error occurred while trying to get course and details for {course_number}: {e}')
        return None


async def update_course_availability(conn: Connection, course_availaibilites: dict[str, str]) -> None:
    availability_tuple = tuple(course_availaibilites.values())
    availability_tuple = availability_tuple[1:] + availability_tuple[:1]

    try:
        async with conn.cursor() as cursor:
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
    except Exception as e:
        print(f'Error occurred while trying to update {availability_tuple}: {e}')


async def fetch_all_course_numbers_and_names(conn: Connection) -> list[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT course_number, course_name FROM course_details')
            return await cursor.fetchall()
    except Exception as e:
        print(f'DB error occurred while attempting to fetch all courses: {e}')
        return []


async def add_user_interest(conn: Connection, user_interests_tuple: tuple) -> None:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO user_interests VALUES (?, ?, ?)', user_interests_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add user interest {user_interests_tuple}: {e}')


async def remove_user_interest(conn: Connection, user_id: str, course_number: str) -> int:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM user_interests WHERE user_id = ? AND course_number = ?', (user_id, course_number))
            if cursor.rowcount == 0:
                return -1

            await cursor.execute('SELECT COUNT(*) FROM user_interests WHERE course_number = ?', (course_number,))
            (remaining_users_interested, ) = await cursor.fetchone()
            if remaining_users_interested == 0:
                await cursor.execute('DELETE FROM course_params WHERE course_number = ?', (course_number,))

            await conn.commit()
            return remaining_users_interested
    except Exception as e:
        print(f'DB error occurred while attempting to remove a user interest for {course_number}: {e}')
        return -1


async def fetch_user_interests(conn: Connection, user_id: str) -> list[Row]:
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
        print(f'DB error occurred while attempting to fetch all user interests: {e}')
        return []


async def fetch_all_users_and_channels_for_course(conn: Connection, course_number: str) -> list[Row]:
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT user_id, channel_id FROM user_interests WHERE course_number = ?', (course_number,))
            return await cursor.fetchall()
    except Exception as e:
        print(f'DB error occurred while attempting to fetch all users interested in {course_number}: {e}')
        return []