from psycopg_pool import ConnectionPool
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DB_PASS = os.getenv("DB_PASS")
pool = ConnectionPool(
    f"host={os.getenv('DB_HOST')} "
    f"port={os.getenv('DB_PORT')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASS')}",
    min_size = 2,
    max_size = 10
)


def get_connection():
    with pool.connection() as conn:
        yield conn