from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import psycopg

from database import get_connection
app = FastAPI()


class User(BaseModel):
    id : int
    name : str
    email: str
    created_at: datetime

class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

@app.post("/users")
def create_user(user: UserCreate, conn = Depends(get_connection)):

    try:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (name, email)
        VALUES (%s, %s)
        RETURNING id, name, email, created_at
        """, (user.name, user.email))

        row = cursor.fetchone()

        conn.commit()

        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            created_at=row[3]
        )

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()

@app.get("/users", response_model = list[User])
def get_users(conn = Depends(get_connection)):

    cursor = conn.cursor()

    cursor.execute("select * from users")

    rows = cursor.fetchall()

    users = []

    for row in rows:
        user = User(
            id=row[0],
            name=row[1],
            email=row[2],
            created_at=row[3]
        )
        users.append(user)

    cursor.close()

    return users



@app.get("/users/{user_id}", response_model = User)
def get_user(user_id: int, conn = Depends(get_connection)):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, created_at
        FROM users
        WHERE id = %s
    """, (user_id,))

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail = "user not found"
        )
    cursor.close()

    return User(
        id=row[0],
        name=row[1],
        email=row[2],
        created_at=row[3]
    )


@app.delete("/users/{user_id}")
def delete_user(user_id: int, conn = Depends(get_connection)):

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id = %s
        RETURNING id
    """, (user_id,))

    deleted_user = cursor.fetchone()

    if deleted_user is None:
        conn.rollback()
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    conn.commit()

    cursor.close()

    return {"message": "User deleted", "id": deleted_user[0]}


@app.patch("/users/{user_id}", response_model = User)
def update_user(user_id: int, user: UserUpdate, conn = Depends(get_connection)):

    cursor = conn.cursor()

    cursor.execute("""
            update users
            set name = coalesce(%s,name),
            email = coalesce(%s,email)
            where id = %s
            returning id, name, email, created_at
    """, (user.name, user.email, user_id))

    row = cursor.fetchone()

    if row is None:
        conn.rollback()
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    conn.commit()

    cursor.close()

    return User(
        id=row[0],
        name=row[1],
        email=row[2],
        created_at=row[3]
    )

