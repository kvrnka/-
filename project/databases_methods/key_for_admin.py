import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "key_for_admin.db")


def create_db_key():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS key_for_admin (
        creator_tg_id INTEGER UNIQUE,
        key_ INTEGER,
        date_of_creation TEXT,
        type_admin TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_key(tg_id, new_key, type_admin):
    create_db_key()

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO key_for_admin (creator_tg_id, key_, date_of_creation, type_admin) VALUES (?, ?, ?, ?)",
                   (tg_id, new_key, formatted_time, type_admin))

    conn.commit()
    conn.close()


def search_key(key_):
    create_db_key()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM key_for_admin WHERE key_ = ?", (key_,))
    keys = cursor.fetchall()  # возможно здесь надо fetchall

    conn.close()

    if not keys:
        return False

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    date_now = datetime.strptime(formatted_time, "%Y-%m-%d %H:%M:%S")

    for res in keys:
        date_past_str = res[2]
        date_past = datetime.strptime(date_past_str, "%Y-%m-%d %H:%M:%S")
        diff = date_now - date_past
        if diff <= timedelta(days = 3):
            return True, res[-1]

    return False
