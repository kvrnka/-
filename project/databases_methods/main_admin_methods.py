import sqlite3
import os
from users_methods import get_user

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "main_admin.db")


def create_db_main_admin():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_admin (
        tg_id INTEGER UNIQUE, 
        tg_username TEXT,
        groups_of_student TEXT,
        full_name TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_main_admin(tg_id, tg_username, groups_of_student, full_name):
    create_db_main_admin()

    user = get_user(tg_id)
    if user:
        full_name = user[3]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO main_admin " "(tg_id, tg_username, groups_of_student, full_name) "
                   "VALUES (?, ?, ?, ?)", (tg_id, tg_username, groups_of_student, full_name))

    conn.commit()
    conn.close()


def get_main_admin(tg_id):
    create_db_main_admin()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM main_admin WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()

    conn.close()
    return user


def get_list_of_main_admin():
    create_db_main_admin()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM main_admin")
    admins = cursor.fetchall()

    conn.close()

    list_of_admin = ''

    for i in range(len(admins)):
        list_of_admin += f"{i + 1}. Имя пользователя: @" + admins[i][1] + '\n'
        list_of_admin += "Имя: " + admins[i][3] + '\n'
        list_of_admin += '\n'

    return list_of_admin


def delete_main_admin_by_username(tg_usernames):
    create_db_main_admin()
    tg_user = tg_usernames.split(", ")

    deleted_rows = 0
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for user in tg_user:
        cursor.execute("DELETE FROM main_admin WHERE tg_username = ?", (user,))
        conn.commit()
        deleted_rows += cursor.rowcount

    conn.close()

    return deleted_rows, len(tg_user)
