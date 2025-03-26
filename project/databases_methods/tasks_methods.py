import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "tasks.db")


def create_db_key():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS key_for_admin (
        primary_key INTEGER AUTOINCREMENT,
        key_ INTEGER,
        date_of_creation TEXT
    )
    """)

    conn.commit()
    conn.close()