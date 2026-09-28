from app.repositories import user_repository


def get_user(conn, user_id):

    return user_repository.get_user(conn, user_id)