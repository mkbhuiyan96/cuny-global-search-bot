async def add_course_params(conn, course_tuple):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_params VALUES (?, ?, ?)', course_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course {course_tuple}: {e}')


async def add_course_details(conn, details_tuple):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_details VALUES (?, ?, ?, ?, ?, ?)', details_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course details {details_tuple}: {e}')


async def add_course_availabilities(conn, availabilities_tuple):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO course_availabilities VALUES (?, ?, ?, ?, ?, ?, ?)', availabilities_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add course availabilities {availabilities_tuple}: {e}')


async def add_course(conn, course_tuple, course_details, course_availabilities):
    if len(course_tuple) > 3:
        course_tuple = course_tuple[:3]
    details_tuple = tuple(course_details.values())
    availabilities_tuple = tuple(course_availabilities.values())

    await add_course_params(conn, course_tuple)
    await add_course_details(conn, details_tuple)
    await add_course_availabilities(conn, availabilities_tuple)


async def remove_course(conn, course_number):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM course_params WHERE course_number = ?', (course_number,))
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to remove course_number {course_number}: {e}')


async def get_course_details(conn, course_number):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT course_params.*, course_details.*
                FROM course_params
                JOIN course_details ON course_params.course_number = course_details.course_number
                WHERE course_details.course_number = ?
            """, (course_number,))
            return await cursor.fetchone()
    except Exception as e:
        print(f'Error occurred while trying to get course and details for {course_number}: {e}')
        return None


async def get_course_availability(conn, course_number):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT course_params.*, course_availabilities.*
                FROM course_params
                JOIN course_availabilities ON course_params.course_number = course_availabilities.course_number
                WHERE course_availabilities.course_number = ?
            """, (course_number,))
            return await cursor.fetchone()
    except Exception as e:
        print(f'Error occurred while trying to get course and details for {course_number}: {e}')
        return None


async def update_course_availability(conn, course_availaibilites):
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


async def add_user_interest(conn, user_interests_tuple):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT OR IGNORE INTO user_interests VALUES (?, ?, ?)', user_interests_tuple)
            await conn.commit()
    except Exception as e:
        print(f'DB error occurred while attempting to add user interest {user_interests_tuple}: {e}')


async def remove_user_interest(conn, user_id, course_number):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM user_interests WHERE user_id = ? AND course_number = ?', (user_id, course_number))
            num_deleted_user_interests = cursor.rowcount

            await cursor.execute('SELECT COUNT(*) FROM user_interests WHERE course_number = ?', (course_number,))
            remaining_users_interested = await cursor.fetchone()
            if remaining_users_interested[0] == 0:
                await cursor.execute('DELETE FROM course_params WHERE course_number = ?', (course_number,))
                num_deleted_user_interests *= -1 # A way to indicate that the whole course was deleted from DB.

            await conn.commit()
            return num_deleted_user_interests
    except Exception as e:
        print(f'DB error occurred while attempting to remove a user interest for {course_number}: {e}')
        return None


async def fetch_user_interests(conn, user_id):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT course_number FROM user_interests WHERE user_id = ?', (user_id,))
            course_numbers = await cursor.fetchall()
            return [course_number[0] for course_number in course_numbers]
    except Exception as e:
        print(f'DB error occurred while attempting to fetch all user interests: {e}')
        return None


async def fetch_all_users_and_channels_for_course(conn, course_number):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT user_id, channel_id FROM user_interests WHERE course_number = ?', (course_number,))
            return await cursor.fetchall()
    except Exception as e:
        print(f'DB error occurred while attempting to fetch all users interested in {course_number}: {e}')
        return None