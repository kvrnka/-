import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "admins.db")

from users_methods import get_user


def create_db_admin():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        tg_id INTEGER UNIQUE,
        full_name TEXT,
        groups_of_students TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_admin(tg_id, groups_of_students):
    create_db_admin()

    user = get_user(tg_id)
    full_name = user[3]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO admins (tg_id, full_name, groups_of_students) VALUES (?, ?, ?)",
                   (tg_id, full_name, groups_of_students))

    conn.commit()
    conn.close()


def search_key(key_):
    pass
    # create_db_admin()
    #
    # conn = sqlite3.connect(db_path)
    # cursor = conn.cursor()
    #
    # cursor.execute("SELECT * FROM key_for_admin WHERE key_ = ?", (key_,))
    # keys = cursor.fetchall()  # возможно здесь надо fetchall
    #
    # conn.close()
    #
    # if keys == []:
    #     return False
    #
    # now = datetime.now()
    # formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    #
    # date_now = datetime.strptime(formatted_time, "%Y-%m-%d %H:%M:%S")
    #
    # for res in keys:
    #     date_past_str = res[2]
    #     date_past = datetime.strptime(date_past_str, "%Y-%m-%d %H:%M:%S")
    #     diff = date_now - date_past
    #     if diff <= timedelta(days = 3):
    #         return True
    #
    # return False
