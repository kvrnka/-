import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "users.db")


def create_db_users():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        tg_id INTEGER UNIQUE, 
        tg_username TEXT,
        full_name TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(tg_id, tg_username, full_name):
    create_db_users()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (tg_id, tg_username, full_name) VALUES (?, ?, ?)",
                   (tg_id, tg_username, full_name))

    conn.commit()
    conn.close()


def get_user(tg_id):
    create_db_users()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()

    conn.close()
    return user
