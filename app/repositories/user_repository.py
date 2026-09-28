


# Get all users
def get_users(conn):

    with conn.cursor() as cursor:

        cursor.execute("""
              SELECT id, name, email, created_at
            FROM users
        """
        )

        rows = cursor.fetchall()

    return rows


#  Get user
def get_user(conn, user_id: int):

    with conn.cursor() as cursor:

        cursor.execute("""
            SELECT id, name, email, created_at
            FROM users
            WHERE id = %s
        """, (user_id,))

        row = cursor.fetchone()

    
    return row